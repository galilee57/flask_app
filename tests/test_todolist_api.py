def test_todolist_crud_is_isolated_and_requires_admin_token(client, admin_headers):
    url = "/projects/todolist/api/todolist"

    assert client.get(url).get_json() == []
    assert client.post(url, json={"text": "Protéger les données"}).status_code == 403

    created = client.post(url, json={"text": " Protéger les données "}, headers=admin_headers)
    assert created.status_code == 201
    task = created.get_json()
    assert task["text"] == "Protéger les données"
    assert task["done"] is False
    assert task["created_at"].endswith("+00:00")

    updated = client.put(
        f"{url}/{task['id']}", json={"done": True}, headers=admin_headers
    )
    assert updated.status_code == 200
    assert updated.get_json()["done"] is True

    assert client.delete(f"{url}/{task['id']}", headers=admin_headers).status_code == 204
    assert client.get(url).get_json() == []


def test_todolist_rejects_invalid_or_empty_updates(client, admin_headers):
    url = "/projects/todolist/api/todolist"
    for payload in (None, {}, {"text": ""}, {"text": "x" * 501}):
        response = client.post(url, json=payload, headers=admin_headers)
        assert response.status_code == 400

    created = client.post(url, json={"text": "Une tâche"}, headers=admin_headers).get_json()
    for payload in ({}, {"done": "true"}, {"unexpected": True}):
        response = client.put(f"{url}/{created['id']}", json=payload, headers=admin_headers)
        assert response.status_code == 400


def test_todolist_reports_missing_task(client, admin_headers):
    url = "/projects/todolist/api/todolist/missing"
    assert client.delete(url, headers=admin_headers).status_code == 404
    assert client.put(url, json={"done": True}, headers=admin_headers).status_code == 404


def test_todolist_refuses_writes_when_token_is_not_configured(app):
    app.config["ADMIN_API_TOKEN"] = None
    response = app.test_client().post(
        "/projects/todolist/api/todolist", json={"text": "Tâche"}
    )
    assert response.status_code == 503
