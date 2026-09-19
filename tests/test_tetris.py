from flask import url_for


def test_tetris_card_links_to_registered_blueprint_and_image(app, client):
    card = app.config["PROJECT_CARDS_BY_ID"]["tetris"]
    with app.test_request_context():
        assert card["projetUrl"] == url_for("tetris.home")
        image_url = url_for("static", filename="images/" + card["image"])
    assert card["published"] is True
    assert client.get(card["projetUrl"]).status_code == 200
    assert client.get(image_url).mimetype == "image/png"


def test_tetris_game_controls_and_local_assets(client):
    response = client.get('/projects/tetris/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for marker in ['id="tetris-board"', 'id="speed"', 'value="human"', 'value="ai"', 'id="score"']:
        assert marker in html
    for asset in ['js/engine.js', 'js/tetris.js', 'css/tailwind.css', 'css/tetris.css']:
        assert client.get('/projects/tetris/static/' + asset).status_code == 200
