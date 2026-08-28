import pytest

from app import create_app
from app.extensions import db


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


@pytest.fixture(autouse=True)
def reset_snake_game():
    from app.projects.snake.routes import game

    game.reset()
    yield
    game.reset()
