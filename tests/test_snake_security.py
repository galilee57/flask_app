def test_recording_snake_stats_requires_admin_token_before_game_mutation(client, admin_headers):
    from app.projects.snake.routes import game

    game.fruit = {"x": 6, "y": 5}
    url = "/projects/snake/api/move/right/manual?record=true"

    assert client.post(url).status_code == 403
    assert game.score == 0
    assert game.snake[0] == {"x": 5, "y": 5}

    response = client.post(url, headers=admin_headers)
    assert response.status_code == 200
    assert response.get_json()["score"] == 1
