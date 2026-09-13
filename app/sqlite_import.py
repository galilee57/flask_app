"""Import legacy business tables without changing the SQLite source."""
from pathlib import Path

import click
from sqlalchemy import MetaData, create_engine, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


TABLE_NAMES = ("programmes", "stations", "programme_exercices", "trains", "snake_stats",
               "todo", "saved_pattern")


def import_sqlite(source: Path, *, dry_run: bool = False):
    uri = source.resolve().as_uri() + "?mode=ro&uri=true"
    engine = create_engine("sqlite+pysqlite:///" + uri)
    counts = {}
    try:
        metadata = MetaData()
        with engine.connect() as connection:
            if connection.exec_driver_sql("PRAGMA integrity_check").scalar() != "ok":
                raise ValueError("La base SQLite est endommagée.")
            if connection.exec_driver_sql("PRAGMA foreign_key_check").first():
                raise ValueError("La base SQLite contient des références incohérentes.")
            metadata.reflect(connection)
            # Read the entire source before making any destination changes.
            rows = {
                name: [dict(row) for row in connection.execute(
                    select(metadata.tables[name])).mappings()]
                for name in TABLE_NAMES if name in metadata.tables
            }
        if not rows:
            raise ValueError("Aucune table métier reconnue dans la base SQLite.")
        with db.engine.begin() as destination:
            target = MetaData()
            target.reflect(destination, only=list(rows))
            if destination.dialect.name == "postgresql":
                # Prevent concurrent writes while checking identifiers and sequences.
                names = ", ".join(destination.dialect.identifier_preparer.quote(name)
                                  for name in rows)
                destination.execute(text(f"LOCK TABLE {names} IN SHARE ROW EXCLUSIVE MODE"))
            for name, records in rows.items():
                table = target.tables[name]
                source_columns = set(metadata.tables[name].columns.keys())
                extra = source_columns - set(table.columns.keys())
                ignored = {"exercice_name"} if name == "programme_exercices" else set()
                if extra - ignored:
                    raise ValueError(f"Colonnes non prises en charge dans {name}: {sorted(extra)}")
                existing = {
                    tuple(row[column.name] for column in table.primary_key): dict(row)
                    for row in destination.execute(select(table)).mappings()
                }
                inserted = skipped = 0
                for record in records:
                    record = {key: value for key, value in record.items() if key in table.columns}
                    if name == "programme_exercices":
                        record["exercice_id"] = str(record["exercice_id"])
                    key = tuple(record[column.name] for column in table.primary_key)
                    if key in existing:
                        if any(existing[key][column] != value for column, value in record.items()):
                            raise ValueError(f"Conflit dans {name}, identifiant {key}: import annulé.")
                        skipped += 1
                    else:
                        destination.execute(table.insert().values(**record))
                        inserted += 1
                counts[name] = {"imported": inserted, "existing": skipped}
            if dry_run:
                destination.rollback()
            elif destination.dialect.name == "postgresql":
                for name in rows:
                    table = target.tables[name]
                    if len(table.primary_key.columns) != 1 or "id" not in table.primary_key:
                        continue
                    sequence = destination.execute(text(
                        "SELECT pg_get_serial_sequence(:table, 'id')"), {"table": name}).scalar()
                    if not sequence:
                        continue
                    maximum = destination.execute(select(table.c.id).order_by(
                        table.c.id.desc()).limit(1)).scalar()
                    if maximum is not None:
                        quoted = ".".join(destination.dialect.identifier_preparer.quote(part)
                                          for part in sequence.split("."))
                        destination.execute(text(
                            f"SELECT setval(CAST(:sequence AS regclass), "
                            f"GREATEST(:maximum, (SELECT last_value FROM {quoted})), true)"
                        ), {"sequence": sequence, "maximum": maximum})
        return counts
    finally:
        engine.dispose()


def register_sqlite_import(app):
    @app.cli.command("sqlite-import")
    @click.option("--source", required=True,
                  type=click.Path(exists=True, dir_okay=False, path_type=Path))
    @click.option("--dry-run", is_flag=True, help="Valider puis annuler les insertions.")
    def command(source, dry_run):
        """Import legacy SQLite data into the configured, migrated database."""
        try:
            counts = import_sqlite(source, dry_run=dry_run)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except SQLAlchemyError as exc:
            # Database errors can contain row values or connection credentials.
            raise click.ClickException(
                "Import annulé : vérifier connexion, migrations et contraintes de données."
            ) from exc
        for name, count in counts.items():
            click.echo(f"{name}: {count['imported']} importés, {count['existing']} déjà présents")
        if dry_run:
            click.echo("Simulation terminée ; aucune ligne conservée.")
