"""Build and verify normalized SQLite copies, never writing to the source.

Run with Python (stdlib only): compact_snow_layers.py SOURCE OUTPUT_DIRECTORY.
The output directory must not already contain the named output files.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3


SCHEMA = """
CREATE TABLE stations (
    id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
    latitude REAL NOT NULL, longitude REAL NOT NULL, elevation_m REAL NOT NULL
);
CREATE TABLE snow_sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE snow_imports (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES snow_sources(id),
    source_url TEXT NOT NULL, imported_at TEXT NOT NULL,
    UNIQUE(source_id, source_url, imported_at), UNIQUE(id, source_id)
);
CREATE TABLE snow_daily_observations (
    id INTEGER PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id),
    observed_on TEXT NOT NULL, snow_depth_cm REAL NOT NULL,
    source_id INTEGER NOT NULL REFERENCES snow_sources(id),
    import_id INTEGER NOT NULL,
    FOREIGN KEY(import_id, source_id) REFERENCES snow_imports(id, source_id),
    UNIQUE(station_id, observed_on, source_id)
);
CREATE INDEX ix_snow_daily_observed_on ON snow_daily_observations(observed_on);
-- The composite uniqueness index also supports lookups by station_id.
CREATE VIEW snow_observations AS
SELECT o.id, o.station_id, o.observed_on, o.snow_depth_cm,
       s.name AS source, i.source_url, i.imported_at
FROM snow_daily_observations o
JOIN snow_sources s ON s.id = o.source_id
JOIN snow_imports i ON i.id = o.import_id;
"""


def sha256(path):
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def build_copy(source, destination, winter_only=False):
    # Exclusive creation prevents accidental overwriting, including the source.
    with destination.open('xb'):
        pass
    connection = sqlite3.connect(destination)
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.execute('ATTACH DATABASE ? AS original',
                           (source.as_uri() + '?mode=ro',))
        connection.executescript(SCHEMA)
        condition = "substr(observed_on, 6, 2) IN ('12','01','02','03','04')" if winter_only else '1'
        with connection:
            connection.execute('INSERT INTO stations SELECT * FROM original.stations')
            connection.execute(f'''INSERT INTO snow_sources(name)
                SELECT DISTINCT source FROM original.snow_observations WHERE {condition}''')
            connection.execute(f'''INSERT INTO snow_imports(source_id, source_url, imported_at)
                SELECT DISTINCT s.id, o.source_url, o.imported_at
                FROM original.snow_observations o JOIN snow_sources s ON s.name = o.source
                WHERE {condition}''')
            connection.execute(f'''INSERT INTO snow_daily_observations
                SELECT o.id, o.station_id, o.observed_on, o.snow_depth_cm, s.id, i.id
                FROM original.snow_observations o
                JOIN snow_sources s ON s.name = o.source
                JOIN snow_imports i ON i.source_id = s.id
                    AND i.source_url = o.source_url AND i.imported_at = o.imported_at
                WHERE {condition} ORDER BY o.id''')
        # Compare every reconstructed column in both directions, not only totals.
        columns = 'id, station_id, observed_on, snow_depth_cm, source, source_url, imported_at'
        expected = f'SELECT {columns} FROM original.snow_observations WHERE {condition}'
        actual = f'SELECT {columns} FROM snow_observations'
        for left, right in ((expected, actual), (actual, expected)):
            if connection.execute(f'SELECT 1 FROM ({left} EXCEPT {right}) LIMIT 1').fetchone():
                raise ValueError('Observation verification failed')
        for left, right in (('original.stations', 'stations'), ('stations', 'original.stations')):
            if connection.execute(f'SELECT * FROM {left} EXCEPT SELECT * FROM {right}').fetchone():
                raise ValueError('Station verification failed')
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not connection.execute('PRAGMA foreign_key_check').fetchall()
        count = connection.execute('SELECT count(*) FROM snow_daily_observations').fetchone()[0]
        imports = connection.execute('SELECT count(*) FROM snow_imports').fetchone()[0]
        return {'path': str(destination), 'bytes': destination.stat().st_size,
                'observations': count, 'imports': imports, 'verified_exact': True}
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    directory = args.output_directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    targets = [directory / 'snow_layers_normalized_all.sqlite',
               directory / 'snow_layers_normalized_winter.sqlite']
    report_path = directory / 'report.json'
    if any(path.exists() for path in [*targets, report_path]):
        parser.error('Output already exists; choose a new directory.')
    before = sha256(source)
    copies = []
    for target, winter in zip(targets, (False, True)):
        result = build_copy(source, target, winter)
        copies.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    after = sha256(source)
    report = {'source': str(source), 'source_bytes': source.stat().st_size,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_unchanged': before == after, 'copies': copies}
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    if before != after:
        raise RuntimeError('Source changed during conversion; see report.')
    print('Source SHA-256 unchanged; all rows verified.', flush=True)


if __name__ == '__main__':
    main()
