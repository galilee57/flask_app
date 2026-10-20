import json
from html.parser import HTMLParser

import pytest

from test_portfolio import PageAssets


class Translations(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.value = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.active = dict(attrs).get('id') == 'pp-text'

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.value += data


@pytest.mark.parametrize('lang,title,prey', [
    ('fr', 'PROIES &amp; PRÉDATEURS', 'Proies'),
    ('en', 'PREY &amp; PREDATORS', 'Prey'),
])
def test_simulation_page_and_catalogue(client, lang, title, prey):
    response = client.get('/projects/prey_predator/', query_string={'lang': lang})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert title in html
    assert 'prey-predator-info-dialog' in html
    assert '[i18n]' not in html
    translations = Translations()
    translations.feed(html)
    messages = json.loads(translations.value)
    assert messages['Proies'] == prey
    assert messages['seed'] == ('GRAINE' if lang == 'fr' else 'SEED')
    assert '${' not in ''.join(messages.values())
    assets = PageAssets()
    assets.feed(html)
    for url in assets.urls:
        assert client.get(url).status_code == 200
    card = next(c for c in client.get('/data/cartes').json if c['id'] == 'prey_predator')
    assert client.get('/static/images/' + card['image']).status_code == 200
    lab = client.get('/lab').get_data(as_text=True)
    assert card['titre'][lang] in lab
