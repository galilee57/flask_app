def test_recording_snake_stats_requires_admin_token_before_game_mutation(client, admin_headers):
    from app.projects.snake.snake_game import Game
    game = Game()
    game.fruit = {"x": 6, "y": 5}
    with client.session_transaction() as stored:
        stored["snake_game"] = game.to_dict()
    url = "/projects/snake/api/move/right/manual?record=true"

    assert client.post(url).status_code == 403
    assert client.get("/projects/snake/api/state").get_json() == game.to_dict()

    response = client.post(url, headers=admin_headers)
    assert response.status_code == 200
    assert response.get_json()["score"] == 1
