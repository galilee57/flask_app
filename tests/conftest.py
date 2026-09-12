import socket

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    """Fail immediately if a test tries to contact an external service."""
    def forbidden_connection(*args, **kwargs):
        raise AssertionError("Network access is forbidden in tests; use a mock.")

    monkeypatch.setattr(socket.socket, "connect", forbidden_connection)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden_connection)
    monkeypatch.setattr(socket, "create_connection", forbidden_connection)


@pytest.fixture()
def app(tmp_path):
    application = create_app("testing")
    application.config.update(
        TODOLIST_DATA_PATH=tmp_path / "todolist.json",
        PATTERN_STORAGE_DIR=tmp_path / "patterns",
    )
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers():
    return {"X-Admin-Token": "test-admin-token"}
