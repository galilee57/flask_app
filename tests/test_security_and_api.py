def test_diagnostic_routes_are_hidden_in_non_debug_config(client):
    for path in ("/debug", "/map", "/files-map"):
        assert client.get(path).status_code == 404


def test_security_headers_are_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_programme_write_requires_admin_token(client, admin_headers):
    payload = {
        "name": "Session test",
        "exercices": [{"exercice_id": "Squat", "reps": 5, "weight": 100}],
    }
    url = "/projects/musculation/api/programmes"

    assert client.post(url, json=payload).status_code == 403

    created = client.post(url, json=payload, headers=admin_headers)
    assert created.status_code == 201
    programme_id = created.get_json()["programme_id"]

    listed = client.get(url)
    assert listed.status_code == 200
    assert listed.get_json()[0]["name"] == "Session test"

    assert client.delete(f"{url}/{programme_id}").status_code == 403
    assert client.delete(f"{url}/{programme_id}", headers=admin_headers).status_code == 200


def test_todolist_write_requires_admin_token(client, admin_headers):
    url = "/projects/todolist/api/todolist"
    assert client.post(url, json={"text": "Tâche"}).status_code == 403

    response = client.post(url, json={"text": "Tâche"}, headers=admin_headers)
    assert response.status_code == 201
    assert response.get_json()["text"] == "Tâche"
