import pytest

from test_portfolio import PageAssets


@pytest.mark.parametrize('language', ('fr', 'en'))
def test_gpt_is_public_and_translated(app, client, language):
    card = app.config['PROJECT_CARDS_BY_ID']['gpt_from_scratch']
    assert card['published'] is True
    assert card['made_by'] == 'Human made'
    response = client.get(card['projetUrl'], query_string={'lang': language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert ('Texte de départ' if language == 'fr' else 'Prompt') in html
    assert ('Comprendre GPT' if language == 'fr' else 'Understanding GPT') in html
    page = PageAssets()
    page.feed(html)
    for asset in page.urls:
        assert client.get(asset).status_code == 200, asset
    assert any(c['id'] == 'gpt_from_scratch' for c in client.get('/data/cartes').json)


def test_catalog_has_metrics_without_local_paths(client):
    response = client.get('/projects/gpt_from_scratch/api/models')
    assert response.status_code == 200
    assert len(response.json) >= 7
    for model in response.json:
        assert model['language'] == 'fr'
        assert model['metrics']
        assert model['architecture']['vocab_size'] > 0
    assert '/Users/' not in response.get_data(as_text=True)


@pytest.mark.parametrize('overrides', [
    {'model': '../../private'}, {'prompt': ''}, {'prompt': 'x' * 1001},
    {'tokens': 501}, {'tokens': True}, {'temperature': 0},
    {'temperature': 'warm'}, {'seed': -1}, {'seed': True},
])
def test_invalid_generation_rejected(client, overrides):
    payload = {'model': 'gpt10k', 'prompt': 'il etait ', **overrides}
    assert client.post('/projects/gpt_from_scratch/api/generate', json=payload).status_code == 400


def test_generation_contract(client, monkeypatch):
    from app.projects.gpt_from_scratch import service
    monkeypatch.setattr(service, 'generate', lambda *args: '<script>text</script>')
    response = client.post('/projects/gpt_from_scratch/api/generate', json={'model': 'gpt10k', 'prompt': 'il etait '})
    assert response.status_code == 200
    assert response.json['continuation'] == '<script>text</script>'
    assert response.json['seconds'] >= 0


@pytest.mark.parametrize('error,status', [(BlockingIOError('busy'), 429), (ImportError('torch'), 503), (ValueError('unsupported_characters'), 400)])
def test_generation_errors(client, monkeypatch, error, status):
    from app.projects.gpt_from_scratch import service
    def fail(*args):
        raise error
    monkeypatch.setattr(service, 'generate', fail)
    response = client.post('/projects/gpt_from_scratch/api/generate', json={'model':'gpt10k', 'prompt':'test'})
    assert response.status_code == status


def test_malformed_and_large_requests(client):
    url = '/projects/gpt_from_scratch/api/generate'
    assert client.post(url, data='broken', content_type='application/json').status_code == 400
    assert client.post(url, json=['test']).status_code == 400
    assert client.post(url, data=' ' * 17000, content_type='application/json').status_code == 413


def test_real_character_and_bpe_generation(app):
    pytest.importorskip('torch')
    pytest.importorskip('tokenizers')
    from app.projects.gpt_from_scratch import service
    with app.app_context():
        for model_id in ('gpt10k', 'generaliste_bpe512'):
            output = service.generate(model_id, 'il etait ', 12, 0.8, 42)
            assert output
            assert output == service.generate(model_id, 'il etait ', 12, 0.8, 42)
        with pytest.raises(ValueError, match='unsupported_characters'):
            service.generate('gpt10k', '🙂', 1, .8, 42)
        assert service._LOCK.acquire(blocking=False)
        try:
            with pytest.raises(BlockingIOError):
                service.generate('gpt10k', 'il etait ', 1, .8, 42)
        finally:
            service._LOCK.release()


def test_generation_frequency_is_bounded(client, monkeypatch):
    from app.projects.gpt_from_scratch import service
    monkeypatch.setattr(service, 'generate', lambda *args: 'text')
    for _ in range(6):
        assert client.post('/projects/gpt_from_scratch/api/generate', json={'model':'gpt10k', 'prompt':'il etait '}).status_code == 200
    response = client.post('/projects/gpt_from_scratch/api/generate', json={'model':'gpt10k', 'prompt':'il etait '})
    assert response.status_code == 429
    assert response.json['error'] == 'rate_limit'
