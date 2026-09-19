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


def test_tetris_bilingual_interface_and_info_modal(client):
    import json
    import re

    for lang, labels in [
        ('fr', ['Aux commandes', 'Avancer manuellement', 'Étape suivante',
                'intelligence artificielle explicable', 'Fermer']),
        ('en', ['At the controls', 'Advance manually', 'Next step',
                'Explainable Artificial Intelligence', 'Close']),
    ]:
        html = client.get('/projects/tetris/?lang=' + lang).get_data(as_text=True)
        assert f'<html lang="{lang}">' in html
        assert 'id="tetris-info-dialog"' in html
        assert 'role="dialog"' in html
        for label in labels:
            assert label in html
        messages = json.loads(re.search(
            r'<script id="tetris-translations" type="application/json">(.*?)</script>',
            html, re.S,
        ).group(1))
        assert messages['Reprendre'] == ('Resume' if lang == 'en' else 'Reprendre')
        assert messages['2 · Déplacement à gauche'] == (
            '2 · Move left' if lang == 'en' else '2 · Déplacement à gauche'
        )
        # Both Markdown files must render as content, not missing-page diagnostics.
        assert '<strong>' in html
        assert '[i18n]' not in html
    assert '<html lang="en">' in client.get('/projects/tetris/').get_data(as_text=True)


def test_tetris_dynamic_translations_have_matching_placeholders():
    import re
    from app.projects.tetris.translations import MESSAGES

    assert MESSAGES['fr'].keys() == MESSAGES['en'].keys()
    for key, french in MESSAGES['fr'].items():
        assert french and MESSAGES['en'][key]
        assert set(re.findall(r'\{\w+\}', french)) == set(
            re.findall(r'\{\w+\}', MESSAGES['en'][key])
        )
