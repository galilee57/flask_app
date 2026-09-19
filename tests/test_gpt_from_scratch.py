import pytest
from flask import url_for

from test_admin_drafts import login
from test_portfolio import PageAssets


def test_gpt_draft_is_hidden_from_visitors(client):
    for path in (
        "/projects/gpt_from_scratch/",
        "/projects/gpt_from_scratch/static/js/gpt_from_scratch.js",
        "/static/images/projectGPTFromScratch.svg",
    ):
        assert client.get(path).status_code == 404
    assert all(card["id"] != "gpt_from_scratch" for card in client.get("/data/cartes").json)
    assert "GPT from scratch" not in client.get("/lab").get_data(as_text=True)


@pytest.mark.parametrize("language", ("fr", "en"))
def test_admin_can_preview_gpt_page_and_assets(app, client, language):
    login(client, app)
    card = app.config["PROJECT_CARDS_BY_ID"]["gpt_from_scratch"]
    assert card["published"] is False
    assert card["made_by"] == "Human made"
    with app.test_request_context():
        assert card["projetUrl"] == url_for("gpt_from_scratch.home")
        image_url = url_for("static", filename="images/" + card["image"])
    response = client.get(card["projetUrl"], query_string={"lang": language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "GPT FROM SCRATCH" in html
    assert ("développement local" if language == "fr" else "local development") in html
    page = PageAssets()
    page.feed(html)
    for asset in page.urls:
        assert client.get(asset).status_code == 200, asset
    assert client.get(image_url).mimetype == "image/svg+xml"
    assert "GPT from scratch" in client.get("/lab").get_data(as_text=True)
