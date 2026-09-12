from flask import url_for


def test_tetris_card_links_to_registered_blueprint_and_image(app, client):
    card = app.config["PROJECT_CARDS_BY_ID"]["tetris"]
    with app.test_request_context():
        assert card["projetUrl"] == url_for("tetris.home")
        image_url = url_for("static", filename="images/" + card["image"])
    assert card["published"] is True
    assert client.get(card["projetUrl"]).status_code == 200
    assert client.get(image_url).mimetype == "image/png"
