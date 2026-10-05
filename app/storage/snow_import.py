"""Import a normalized winter archive into the shared, migrated database."""
from datetime import date, datetime, timezone
import hashlib
from pathlib import Path
import sqlite3

import click
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.projects.snow_layers.models import SnowStation, SnowSource, SnowImport, SnowObservation, SnowSeedRun

TABLES = (
    ("stations", SnowStation.__table__),
    ("snow_sources", SnowSource.__table__),
    ("snow_imports", SnowImport.__table__),
    ("snow_daily_observations", SnowObservation.__table__),
)


def _digest(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def _convert(table, row):
    record = dict(row)
    if table.name == "snow_imports":
        imported_at = datetime.fromisoformat(record["imported_at"])
        if imported_at.tzinfo is not None:
            imported_at = imported_at.astimezone(timezone.utc).replace(tzinfo=None)
        record["imported_at"] = imported_at
    if table.name == "snow_daily_observations":
        record["observed_on"] = date.fromisoformat(record["observed_on"])
        if record["observed_on"].month not in (12, 1, 2, 3, 4):
            raise ValueError("L’archive doit contenir uniquement décembre à avril.")
    return record


def import_snow_archive(source: Path, *, dry_run=False, seed_digest=None):
    """Preserve IDs and provenance; abort atomically on any conflicting row."""
    source = source.resolve(strict=True)
    before = _digest(source)
    counts = {}
    original = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    original.row_factory = sqlite3.Row
    try:
        if original.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Archive SQLite endommagée.")
        if original.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Références incohérentes dans l’archive.")
        with db.engine.begin() as destination:
            if destination.dialect.name == "postgresql":
                names = ", ".join(table.name for _, table in TABLES)
                destination.execute(text(f"LOCK TABLE {names} IN SHARE ROW EXCLUSIVE MODE"))
            if seed_digest and destination.execute(select(SnowSeedRun.digest).where(
                    SnowSeedRun.digest == seed_digest)).first():
                return {"tables": {}, "source_sha256": before, "dry_run": dry_run}
            for source_name, table in TABLES:
                columns = ", ".join(column.name for column in table.columns)
                cursor = original.execute(f"SELECT {columns} FROM {source_name} ORDER BY id")
                inserted = skipped = 0
                while batch := cursor.fetchmany(4000):
                    records = [_convert(table, row) for row in batch]
                    ids = [row["id"] for row in records]
                    existing = {row["id"]: dict(row) for row in destination.execute(
                        select(table).where(table.c.id.in_(ids))).mappings()}
                    additions = []
                    for row in records:
                        if row["id"] in existing:
                            if existing[row["id"]] != row:
                                raise ValueError(f"Conflit dans {table.name}, id {row['id']} ; import annulé.")
                            skipped += 1
                        else:
                            additions.append(row)
                    if additions:
                        destination.execute(table.insert(), additions)
                        inserted += len(additions)
                    # Verify every value after type conversion and insertion.
                    persisted = {row["id"]: dict(row) for row in destination.execute(
                        select(table).where(table.c.id.in_(ids))).mappings()}
                    if any(persisted.get(row["id"]) != row for row in records):
                        raise ValueError(f"Vérification échouée dans {table.name}.")
                counts[table.name] = {"imported": inserted, "existing": skipped}
            if _digest(source) != before:
                raise ValueError("L’archive a changé pendant l’import ; opération annulée.")
            if seed_digest:
                destination.execute(SnowSeedRun.__table__.insert().values(digest=seed_digest))
            if dry_run:
                destination.rollback()
            elif destination.dialect.name == "postgresql":
                for _, table in TABLES:
                    # Tables are locked above. Preserve sequence values on repeat imports.
                    sequence = destination.execute(text(
                        "SELECT pg_get_serial_sequence(:table, 'id')"), {"table": table.name}).scalar_one()
                    maximum = destination.execute(select(table.c.id).order_by(table.c.id.desc()).limit(1)).scalar()
                    if maximum is not None:
                        quoted = ".".join(destination.dialect.identifier_preparer.quote(part)
                                          for part in sequence.split("."))
                        destination.execute(text(
                            f"SELECT setval(CAST(:sequence AS regclass), "
                            f"GREATEST(:maximum, (SELECT last_value FROM {quoted})), true)"
                        ), {"sequence": sequence, "maximum": maximum})
        return {"tables": counts, "source_sha256": before, "dry_run": dry_run}
    finally:
        original.close()


def register_snow_import(app):
    @app.cli.command("snow-import")
    @click.option("--source", required=True,
                  type=click.Path(exists=True, dir_okay=False, path_type=Path))
    @click.option("--dry-run", is_flag=True, help="Vérifier puis annuler les insertions.")
    def command(source, dry_run):
        """Import normalized December–April SQLite history without changing it."""
        try:
            result = import_snow_archive(source, dry_run=dry_run)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except (SQLAlchemyError, sqlite3.Error) as exc:
            raise click.ClickException("Import annulé : vérifier archive, migrations et connexion.") from exc
        for name, count in result["tables"].items():
            click.echo(f"{name}: {count['imported']} importés, {count['existing']} déjà présents")
        click.echo("Toutes les valeurs vérifiées ; archive source inchangée.")
        if dry_run:
            click.echo("Simulation : aucune insertion conservée.")
