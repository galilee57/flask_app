import math

import pytest

from app.projects.shortest_path.engine import DATASETS, load_graph, search
from test_portfolio import PageAssets


@pytest.mark.parametrize('language,title', [('fr', 'LE PLUS COURT CHEMIN'), ('en', 'THE SHORTEST PATH')])
def test_page_catalogue_and_assets(client, language, title):
    response = client.get('/projects/shortest_path/', query_string={'lang': language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert title in html
    assert 'shortest-path-info-dialog' in html
    assert '[i18n]' not in html
    assets = PageAssets()
    assets.feed(html)
    for url in assets.urls:
        assert client.get(url).status_code == 200
    card = next(c for c in client.get('/data/cartes').json if c['id'] == 'shortest_path')
    assert card['made_by'] == 'AI made'
    assert client.get('/static/images/' + card['image']).status_code == 200
    assert 'Shortest Path' in client.get('/lab').get_data(as_text=True)


@pytest.mark.parametrize('size', DATASETS)
def test_algorithms_match_independent_reference(size):
    nodes, edges = load_graph(size)
    # Bellman-Ford reference, independent of the priority-queue implementation.
    distances = {n: math.inf for n in nodes}
    distances[0] = 0
    for _ in range(len(nodes)-1):
        changed = False
        for a, b, weight in edges:
            for u, v in ((a, b), (b, a)):
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    changed = True
        if not changed:
            break
    for algorithm in ('astar', 'dijkstra'):
        result = search(nodes, edges, 0, 1, algorithm)
        assert result['cost'] == pytest.approx(distances[1])
        assert result['path'][0] == 0 and result['path'][-1] == 1
        weights = {frozenset((a,b)): w for a,b,w in edges}
        assert sum(weights[frozenset(pair)] for pair in zip(result['path'], result['path'][1:])) == pytest.approx(result['cost'])
        assert result['steps'][-1]['current'] == 1


def test_same_node_and_unreachable():
    nodes = {0:(0,0), 1:(1,1)}
    assert search(nodes, [], 0, 0)['cost'] == 0
    result = search(nodes, [], 0, 1)
    assert result['cost'] is None and result['path'] == []


@pytest.mark.parametrize('query', ['graph=999', 'graph=../../etc/passwd', 'start=-1', 'goal=999', 'algorithm=invalid', 'goal=nan'])
def test_api_rejects_invalid_parameters(client, query):
    response = client.get('/projects/shortest_path/api/solve?' + query)
    assert response.status_code == 400
    assert response.json == {'error':'invalid_parameters'}


def test_solve_api_is_stateless(client):
    url = '/projects/shortest_path/api/solve'
    first = client.get(url).json
    assert first['path'][0:1] == [0]
    assert len(first['nodes']) == 13
    assert client.get(url + '?start=1&goal=0').json['cost'] == pytest.approx(first['cost'])
    assert client.get(url).json == first
