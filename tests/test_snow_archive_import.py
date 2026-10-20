import sqlite3
from datetime import date

import pytest
from sqlalchemy import event, func, select

from app.extensions import db
from app.projects.snow_layers.models import SnowImport, SnowObservation, SnowStation
from app.projects.snow_layers.repository import load_station_means
from app.storage.snow_import import import_snow_archive
from scripts.compact_snow_layers import SCHEMA, sha256


@pytest.fixture()
def archive(tmp_path):
    path = tmp_path / 'normalized.sqlite'
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.executescript('''
            INSERT INTO stations VALUES(1, 'meribel', 'Méribel', 45.4, 6.5, 1450);
            INSERT INTO snow_sources VALUES(1, 'ERA5-Land');
            INSERT INTO snow_imports VALUES(1, 1, 'https://example.org/history', '2026-09-11 12:30:00');
            INSERT INTO snow_daily_observations VALUES(10, 1, '2024-12-01', 12.34567, 1, 1);
            INSERT INTO snow_daily_observations VALUES(20, 1, '2025-01-01', 0.0, 1, 1);
        ''')
    return path


def test_archive_import_is_exact_idempotent_and_visible(app, client, archive):
    before = sha256(archive)
    dry = import_snow_archive(archive, dry_run=True)
    assert dry['tables']['snow_daily_observations']['imported'] == 2
    assert db.session.scalar(select(func.count()).select_from(SnowObservation)) == 0
    db.session.remove()
    first = import_snow_archive(archive)
    second = import_snow_archive(archive)
    assert first['tables']['snow_daily_observations']['imported'] == 2
    assert second['tables']['snow_daily_observations'] == {'imported': 0, 'existing': 2}
    assert db.session.get(SnowObservation, 10).snow_depth_cm == 12.34567
    assert db.session.get(SnowImport, 1).imported_at.isoformat() == '2026-09-11T12:30:00'
    result = client.get('/projects/snow_layers/api/snow-depth').get_json()
    assert not result['is_demo'] and result['collected_at'] == '2026-09-11T12:30:00'
    assert result['seasons']['2024-2025'][0]['depth_cm'] == 12.34567
    assert sha256(archive) == before


def test_conflict_rolls_back_all_tables(app, archive):
    import_snow_archive(archive)
    with sqlite3.connect(archive) as connection:
        connection.execute("INSERT INTO stations VALUES(2, 'tignes', 'Tignes', 45, 6, 2100)")
        connection.execute('UPDATE snow_daily_observations SET snow_depth_cm=99 WHERE id=20')
    with pytest.raises(ValueError, match='Conflit'):
        import_snow_archive(archive)
    assert db.session.get(SnowStation, 2) is None
    assert db.session.get(SnowObservation, 20).snow_depth_cm == 0


def test_winter_import_rejects_summer_atomically(app, archive):
    with sqlite3.connect(archive) as connection:
        connection.execute("UPDATE snow_daily_observations SET observed_on='2025-07-01' WHERE id=20")
    with pytest.raises(ValueError, match='décembre'):
        import_snow_archive(archive)
    assert db.session.scalar(select(func.count()).select_from(SnowStation)) == 0


def test_comparison_aggregates_with_one_query(app, archive):
    import_snow_archive(archive)
    queries = []
    def record(*args):
        queries.append(args[2])
    event.listen(db.engine, 'before_cursor_execute', record)
    try:
        assert load_station_means(db.session) == {'meribel': {'2024-2025': 6.2}}
    finally:
        event.remove(db.engine, 'before_cursor_execute', record)
    assert len(queries) == 1


def test_weather_reimport_updates_depth_and_provenance(client, app, archive, admin_headers, monkeypatch):
    from app.projects.snow_layers import routes
    import_snow_archive(archive)
    monkeypatch.setattr(routes, 'SOURCE_NAME', 'ERA5-Land')
    monkeypatch.setattr(routes, 'fetch_daily_snow_depth', lambda **kw: (
        [(date(2024, 12, 1), 50.0)], 'https://example.org/new'))
    response = client.post('/projects/snow_layers/api/snow-depth/import',
        json={'station': 'meribel', 'season': '2024-2025'}, headers=admin_headers)
    assert response.status_code == 200
    assert db.session.scalar(select(func.count()).select_from(SnowImport)) == 2
    assert db.session.scalar(select(func.count()).select_from(SnowObservation)) == 2
    observation = db.session.get(SnowObservation, 10)
    assert observation.snow_depth_cm == 50.0
    assert db.session.get(SnowImport, observation.import_id).source_url == 'https://example.org/new'


def test_bundled_seed_runs_once_and_preserves_future_updates(app, archive, tmp_path):
    import gzip
    import json
    from app.storage.snow_seed import seed_history
    from app.storage.snow_import import _digest
    from app.projects.snow_layers.models import SnowSeedRun
    folder = tmp_path / 'seed'
    folder.mkdir()
    counts = {}
    with sqlite3.connect(archive) as connection, gzip.open(folder / 'winter_history.jsonl.gz', 'wt') as stream:
        connection.row_factory = sqlite3.Row
        for name in ('stations', 'snow_sources', 'snow_imports', 'snow_daily_observations'):
            rows = [dict(row) for row in connection.execute(f'SELECT * FROM {name}')]
            counts[name] = len(rows)
            stream.write(json.dumps({'table': name, 'rows': rows}) + '\n')
    (folder / 'manifest.json').write_text(json.dumps({'sha256': _digest(folder / 'winter_history.jsonl.gz'), 'counts': counts}))
    assert seed_history(folder)
    assert db.session.scalar(select(func.count()).select_from(SnowSeedRun)) == 1
    row = db.session.get(SnowObservation, 10)
    row.snow_depth_cm = 99
    db.session.commit()
    assert not seed_history(folder)
    assert db.session.get(SnowObservation, 10).snow_depth_cm == 99
