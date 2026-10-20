from datetime import date

from app.projects.snow_layers import routes

PREFIX = '/projects/snow_layers'


def test_page_catalog_and_demo(client):
    page = client.get(PREFIX + '/')
    assert page.status_code == 200
    assert b'snow-layers-info' in page.data
    assert b'/projects/snow_layers/static/' in page.data
    assert b'Cod' in client.get('/lab').data
    stations = client.get(PREFIX + '/api/stations').get_json()['stations']
    assert len(stations) == 46
    demo = client.get(PREFIX + '/api/snow-depth').get_json()
    assert demo['is_demo'] and demo['seasons'] and demo['unit'] == 'cm'
    assert client.get(PREFIX + '/api/snow-depth?station=unknown').status_code == 404
    assert client.get(PREFIX + '/api/snow-depth?station=tignes').get_json()['seasons'] == {}
    assert client.get(PREFIX + '/api/comparison?station=meribel').status_code == 400
    assert client.get(PREFIX + '/api/comparison?station=meribel&station=tignes').get_json()['seasons'] == []


def test_import_authorization_validation_and_persistence(client, admin_headers, monkeypatch):
    url = PREFIX + '/api/snow-depth/import'
    body = {'station': 'tignes', 'season': '2024-2025'}
    assert client.post(url, json=body).status_code == 403
    assert client.post(url, json={'station': 'tignes', 'season': 'bad'}, headers=admin_headers).status_code == 400
    monkeypatch.setattr(routes, 'fetch_daily_snow_depth', lambda **kw: ([(date(2024, 12, 1), 42.0)], 'https://example.com/weather'))
    result = client.post(url, json=body, headers=admin_headers)
    assert result.status_code == 200 and result.get_json()['partial']
    data = client.get(PREFIX + '/api/snow-depth?station=tignes').get_json()
    assert not data['is_demo']
    assert data['seasons']['2024-2025'][0]['depth_cm'] == 42.0
    comparison = client.get(PREFIX + '/api/comparison?station=meribel&station=tignes').get_json()
    assert comparison['stations']['tignes']['values']['2024-2025'] == 42.0
