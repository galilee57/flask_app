"""Load the bundled public weather dataset once, after schema migrations."""
import gzip
import json
from pathlib import Path
import sqlite3
import tempfile

import click
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.projects.snow_layers.models import SnowSeedRun
from app.storage.snow_import import _digest, import_snow_archive

DATA_DIR = Path(__file__).resolve().parents[1] / 'projects/snow_layers/data'
# A temporary interchange file, never an application database.
SCHEMA = '''
CREATE TABLE stations (id INTEGER PRIMARY KEY, slug TEXT, name TEXT,
    latitude REAL, longitude REAL, elevation_m REAL);
CREATE TABLE snow_sources (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE snow_imports (id INTEGER PRIMARY KEY, source_id INTEGER,
    source_url TEXT, imported_at TEXT);
CREATE TABLE snow_daily_observations (id INTEGER PRIMARY KEY, station_id INTEGER,
    observed_on TEXT, snow_depth_cm REAL, source_id INTEGER, import_id INTEGER);
'''


def seed_history(data_dir=DATA_DIR):
    manifest = json.loads((data_dir / 'manifest.json').read_text())
    digest = manifest['sha256']
    with db.engine.connect() as connection:
        if connection.execute(select(SnowSeedRun.digest).where(SnowSeedRun.digest == digest)).first():
            return False
    archive = data_dir / 'winter_history.jsonl.gz'
    if _digest(archive) != digest:
        raise ValueError('Empreinte de l’export météo incorrecte.')
    with tempfile.TemporaryDirectory(prefix='snow-seed-') as directory:
        path = Path(directory) / 'history.sqlite'
        with sqlite3.connect(path) as connection:
            connection.executescript(SCHEMA)
            columns = {name: [row[1] for row in connection.execute(f'PRAGMA table_info({name})')]
                       for name in ('stations', 'snow_sources', 'snow_imports', 'snow_daily_observations')}
            counts = dict.fromkeys(columns, 0)
            with gzip.open(archive, 'rt', encoding='utf-8') as stream:
                for line in stream:
                    block = json.loads(line)
                    name = block['table']
                    if name not in columns:
                        raise ValueError('Table météo inconnue.')
                    fields = columns[name]
                    connection.executemany(
                        f"INSERT INTO {name} ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",
                        [[row[field] for field in fields] for row in block['rows']])
                    counts[name] += len(block['rows'])
            if counts != manifest['counts']:
                raise ValueError('Nombre de lignes météo incorrect.')
        import_snow_archive(path, seed_digest=digest)
    return True


def register_snow_seed(app):
    @app.cli.command('snow-seed')
    def command():
        """Import the bundled public winter dataset exactly once."""
        try:
            imported = seed_history()
        except (ValueError, OSError, SQLAlchemyError, sqlite3.Error) as exc:
            original = getattr(exc, 'orig', exc)
            code = getattr(original, 'sqlstate', None) or getattr(original, 'sqlite_errorname', None) or getattr(original, 'errno', None)
            detail = str(exc) if isinstance(exc, ValueError) else ''
            raise click.ClickException(
                f'Import météo annulé ({type(original).__name__}, code={code}). {detail}'
            ) from exc
        click.echo('Historique météo importé et vérifié.' if imported else 'Historique météo déjà importé.')
