import hashlib
import sqlite3

import pytest

from app.extensions import db
from app.projects.musculation.models import Programme, ProgrammeExercice
from app.sqlite_import import import_sqlite


@pytest.fixture
def legacy_database(tmp_path):
    source = tmp_path / "legacy.db"
    with sqlite3.connect(source) as connection:
        connection.executescript("""
            CREATE TABLE programmes (
                id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL,
                description TEXT, created_at DATETIME
            );
            CREATE TABLE programme_exercices (
                id INTEGER PRIMARY KEY,
                programme_id INTEGER NOT NULL REFERENCES programmes(id),
                exercice_id INTEGER NOT NULL, reps INTEGER NOT NULL,
                weight INTEGER NOT NULL
            );
            INSERT INTO programmes VALUES (7, 'Programme importé', NULL, '2025-01-02 10:30:00');
            INSERT INTO programme_exercices VALUES (12, 7, 'Développé couché barre', 8, 40);
        """)
    return source


def test_import_preserves_names_dates_source_and_is_idempotent(app, legacy_database):
    digest = hashlib.sha256(legacy_database.read_bytes()).digest()
    counts = import_sqlite(legacy_database)
    assert counts['programmes']['imported'] == 1
    assert db.session.get(Programme, 7).created_at.year == 2025
    assert db.session.get(ProgrammeExercice, 12).exercice_id == 'Développé couché barre'
    counts = import_sqlite(legacy_database)
    assert counts['programme_exercices'] == {'imported': 0, 'existing': 1}
    assert hashlib.sha256(legacy_database.read_bytes()).digest() == digest


def test_conflict_rolls_back_prior_insertions(app, legacy_database):
    db.session.add(Programme(id=7, name='Programme importé'))
    db.session.add(ProgrammeExercice(id=12, programme_id=7, exercice_id='Autre', reps=8, weight=40))
    db.session.commit()
    with sqlite3.connect(legacy_database) as connection:
        connection.execute('UPDATE programmes SET created_at = NULL')
        connection.execute("INSERT INTO programmes VALUES (1, 'Nouveau', NULL, NULL)")
    with pytest.raises(ValueError, match='Conflit'):
        import_sqlite(legacy_database)
    db.session.expire_all()
    assert db.session.get(Programme, 1) is None
    assert db.session.get(ProgrammeExercice, 12).exercice_id == 'Autre'


def test_dry_run_does_not_persist_data(app, legacy_database):
    counts = import_sqlite(legacy_database, dry_run=True)
    assert counts['programme_exercices']['imported'] == 1
    assert db.session.get(Programme, 7) is None
