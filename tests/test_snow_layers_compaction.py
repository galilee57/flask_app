import sqlite3

import pytest

from scripts.compact_snow_layers import build_copy, sha256


def test_compaction_preserves_values_provenance_and_source(tmp_path):
    source = tmp_path / 'original.sqlite'
    with sqlite3.connect(source) as connection:
        connection.executescript('''
            CREATE TABLE stations(id INTEGER PRIMARY KEY, slug TEXT, name TEXT,
                latitude REAL, longitude REAL, elevation_m REAL);
            CREATE TABLE snow_observations(id INTEGER PRIMARY KEY, station_id INTEGER,
                observed_on TEXT, snow_depth_cm REAL, source TEXT,
                source_url TEXT, imported_at TEXT);
            INSERT INTO stations VALUES(1, 'meribel', 'Méribel', 45.4, 6.5, 1450);
        ''')
        connection.executemany('INSERT INTO snow_observations VALUES(?,?,?,?,?,?,?)', [
            (1, 1, '2024-12-01', 12.34567, 'model', 'https://example.org/a', '2025-01-01'),
            (2, 1, '2025-01-01', 0.0, 'model', 'https://example.org/a', '2025-01-01'),
            (3, 1, '2025-06-01', 1.25, 'model', 'https://example.org/b', '2025-07-01'),
        ])
    initial_hash = sha256(source)
    all_path = tmp_path / 'all.sqlite'
    full = build_copy(source, all_path)
    winter = build_copy(source, tmp_path / 'winter.sqlite', winter_only=True)
    assert full['observations'] == 3 and full['imports'] == 2
    assert winter['observations'] == 2 and winter['imports'] == 1
    assert sha256(source) == initial_hash
    with sqlite3.connect(all_path) as connection:
        assert connection.execute('SELECT snow_depth_cm FROM snow_observations WHERE id=1').fetchone() == (12.34567,)
    with pytest.raises(FileExistsError):
        build_copy(source, all_path)
    with pytest.raises(FileExistsError):
        build_copy(source, source)
    assert sha256(source) == initial_hash
