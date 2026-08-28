def test_saving_shared_pattern_requires_admin_and_uses_instance_storage(app, client, admin_headers, tmp_path):
    url = "/projects/game_of_life/save"
    assert client.post(url, json={"name": "glider"}).status_code == 403

    response = client.post(url, json={"name": "glider"}, headers=admin_headers)
    assert response.status_code == 200
    assert (tmp_path / "patterns" / "glider.json").is_file()
    assert client.get("/projects/game_of_life/saved").get_json() == {"patterns": ["glider"]}


def test_pattern_names_must_be_safe_and_bounded(client, admin_headers):
    response = client.post(
        "/projects/game_of_life/save", json={"name": "!" * 81}, headers=admin_headers
    )
    assert response.status_code == 400
