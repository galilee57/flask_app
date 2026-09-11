"""Persistence and refusal paths must never damage stored tasks."""

import pytest

from app.projects.todolist.repository import TodoRepository


URL = "/projects/todolist/api/todolist"


def test_created_task_can_be_read_from_a_new_repository(app, client, admin_headers):
    response = client.post(URL, json={"text": "Tâche durable"}, headers=admin_headers)
    assert response.status_code == 201
    repository = TodoRepository(app.config["TODOLIST_DATA_PATH"])
    assert repository.list() == [response.get_json()]


@pytest.mark.parametrize("method", ("post", "put", "delete"))
@pytest.mark.parametrize("headers", ({}, {"X-Admin-Token": "wrong-token"}))
def test_rejected_write_does_not_change_persisted_tasks(app, client, admin_headers, method, headers):
    task = client.post(URL, json={"text": "À préserver"}, headers=admin_headers).get_json()
    path = app.config["TODOLIST_DATA_PATH"]
    before = path.read_bytes()
    target = URL if method == "post" else f"{URL}/{task['id']}"
    response = client.open(target, method=method.upper(), headers=headers, json={"text": "Modifiée"})
    assert response.status_code == 403
    assert path.read_bytes() == before


@pytest.mark.parametrize("payload", ("invalid json", '{"not": "a list"}'))
def test_corrupted_storage_is_reported_and_preserved(tmp_path, payload):
    path = tmp_path / "tasks.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(RuntimeError, match="stockage des tâches"):
        TodoRepository(path).list()
    assert path.read_text(encoding="utf-8") == payload


def test_oversized_request_is_rejected_without_creating_storage(app, client, admin_headers):
    response = client.post(
        URL, data='{"text":"' + "x" * app.config["MAX_CONTENT_LENGTH"] + '"}',
        content_type="application/json", headers=admin_headers,
    )
    assert response.status_code == 413
    assert not app.config["TODOLIST_DATA_PATH"].exists()
