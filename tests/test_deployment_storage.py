"""Deployment contracts: durability, visitor isolation and migration lifecycle."""
import json

from flask_migrate import upgrade, downgrade
from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.config import ProdConfig

TODO_URL = "/projects/todolist/api/todolist"
SNAKE_URL = "/projects/snake/api"


def test_sql_todo_updates_preserve_other_fields_and_reject_unauthorized(app, client, admin_headers):
    app.config["TODOLIST_DATA_PATH"] = None
    first = client.post(TODO_URL, json={"text": "first"}, headers=admin_headers).json
    second = client.post(TODO_URL, json={"text": "second"}, headers=admin_headers).json
    assert client.put(f"{TODO_URL}/{first['id']}", json={"done": True}).status_code == 403
    assert client.put(f"{TODO_URL}/{first['id']}", json={"done": True}, headers=admin_headers).json["text"] == "first"
    assert client.put(f"{TODO_URL}/{first['id']}", json={"text": "renamed"}, headers=admin_headers).json["done"] is True
    assert second in app.test_client().get(TODO_URL).json
    assert client.delete(f"{TODO_URL}/unknown", headers=admin_headers).status_code == 404


def test_database_patterns_are_shared_and_loadable(app, client, admin_headers):
    app.config["PATTERN_STORAGE_DIR"] = None
    base = "/projects/game_of_life"
    client.post(base + "/toggle", json={"row": 1, "col": 1})
    assert client.post(base + "/save", json={"name": "shared"}, headers=admin_headers).status_code == 200
    other = app.test_client()
    assert other.get(base + "/saved").json == {"patterns": ["shared"]}
    assert other.post(base + "/load", json={"name": "shared"}).json["grid"][1][1] == 1
    assert other.post(base + "/load", json={"name": "missing"}).status_code == 404


def test_games_and_large_grids_survive_new_app_instance(tmp_path, monkeypatch):
    from app.config import TestingConfig
    monkeypatch.setattr(TestingConfig, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'shared.db'}")
    # Exercise runtime persistence independently of catalogue publication.
    first_app = create_app("testing")
    first_app.config["PROJECT_CARDS_BY_ID"]["game_of_life_3d"]["published"] = True
    with first_app.app_context():
        db.create_all()
    first = first_app.test_client()
    first.post(SNAKE_URL + "/move/right/manual")
    universe = first.get("/projects/game_of_life_3d/state").json
    first.post("/projects/game_of_life/grid", json={"rows": 300, "cols": 300})
    cookie = first.get_cookie("session").value
    assert len(cookie) < 200
    other = create_app("testing").test_client()
    other.application.config["PROJECT_CARDS_BY_ID"]["game_of_life_3d"]["published"] = True
    other.set_cookie("session", cookie)
    assert other.get(SNAKE_URL + "/state").json["total_steps"] == 1
    assert other.get("/projects/game_of_life_3d/state").json == universe
    assert other.get("/projects/game_of_life/state").json["rows"] == 300
    fresh = first_app.test_client()
    assert fresh.get(SNAKE_URL + "/state").json["total_steps"] == 0
    assert fresh.get("/projects/game_of_life_3d/state").json["universe_id"] != universe["universe_id"]
    assert other.post("/projects/game_of_life_3d/next", json={"universe_id": "old", "version": 0}).status_code == 409


def test_cookie_tampering_does_not_load_another_visitor(client, app):
    client.post(SNAKE_URL + "/move/right/manual")
    forged = app.test_client()
    forged.set_cookie("session", client.get_cookie("session").value + "tampered")
    assert forged.get(SNAKE_URL + "/state").json["total_steps"] == 0


def test_health_and_expired_session_cleanup(app, client):
    from app.runtime_models import RuntimeSession
    assert client.get("/health/live").json == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    db.session.add(RuntimeSession(id="expired", payload="{}", expires_at=1, version=1))
    db.session.commit()
    assert app.test_cli_runner().invoke(args=["sessions-prune"]).exit_code == 0
    assert db.session.get(RuntimeSession, "expired") is None
    db.session.remove()
    db.drop_all()
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 503


def test_runtime_path_is_passed_to_flask(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_INSTANCE_PATH", str(tmp_path / "runtime"))
    assert create_app("testing").instance_path == str(tmp_path / "runtime")


def test_container_mode_rejects_local_database(monkeypatch):
    monkeypatch.setattr(ProdConfig, "CONTAINER_MODE", True)
    monkeypatch.setattr(ProdConfig, "SECRET_KEY", "test-secret")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import pytest
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        create_app("production")


def test_import_is_idempotent_and_preserves_source(app, tmp_path):
    path = tmp_path / "legacy.json"
    original = [{"id": "legacy", "text": "preserved", "done": False, "created_at": "2026-09-12T00:00:00Z"}]
    path.write_text(json.dumps(original))
    before = path.read_bytes()
    runner = app.test_cli_runner()
    assert runner.invoke(args=["storage-import", "--todos", str(path)]).exit_code == 0
    assert "0 éléments" in runner.invoke(args=["storage-import", "--todos", str(path)]).output
    assert path.read_bytes() == before
    from app.runtime_models import Todo
    assert db.session.get(Todo, "legacy").text == "preserved"


def test_migrations_create_runtime_schema_and_allow_downgrade(tmp_path, monkeypatch):
    from app.config import TestingConfig
    monkeypatch.setattr(TestingConfig, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'migrations.db'}")
    with create_app("testing").app_context():
        upgrade()
        assert {"todo", "runtime_session", "saved_pattern"} <= set(inspect(db.engine).get_table_names())
        downgrade(revision="9ad4c7e0b812")
        assert "todo" not in inspect(db.engine).get_table_names()
        upgrade()


def test_docker_definitions_stay_identical():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert (root / "Dockerfile").read_bytes() == (root / "Dockerfile.vercel").read_bytes()
