import time

from werkzeug.security import generate_password_hash


def login(client, app):
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('preview-password')
    client.get('/admin')
    with client.session_transaction() as session:
        token = session['admin_csrf']
    return client.post('/admin', data={'csrf_token': token, 'username': app.config['ADMIN_USERNAME'], 'password': 'preview-password'})


def test_drafts_are_private_and_published_projects_remain_public(client):
    assert client.get('/projects/projet_test/').status_code == 404
    assert client.get('/projects/game_of_life_3d/state').status_code == 404
    assert client.get('/projects/charts/static/js/charts.js').status_code == 404
    assert client.get('/static/images/projectTest.jpg').status_code == 404
    assert client.get('/static/data/cartes.json').status_code == 404
    cards = client.get('/data/cartes').json
    assert cards and all(card['published'] for card in cards)
    assert client.get('/projects/tetris/').status_code == 200


def test_login_preview_logout_and_session_isolation(client, app):
    assert login(client, app).status_code == 302
    assert client.get('/projects/projet_test/').status_code == 200
    response = client.get('/data/cartes')
    assert any(not card['published'] for card in response.json)
    assert response.headers['Cache-Control'] == 'private, no-store'
    assert 'noindex' in response.headers['X-Robots-Tag']
    assert app.test_client().get('/projects/projet_test/').status_code == 404
    with client.session_transaction() as session:
        token = session['admin_csrf']
    assert client.post('/admin/logout', data={'csrf_token': token}).status_code == 302
    assert client.get('/projects/projet_test/').status_code == 404


def test_csrf_wrong_password_expiry_and_password_rotation(client, app):
    assert client.post('/admin', data={'password': 'preview-password'}).status_code == 400
    login(client, app)
    with client.session_transaction() as session:
        session['admin_until'] = time.time() - 1
    assert client.get('/projects/projet_test/').status_code == 404
    login(client, app)
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('replacement')
    assert client.get('/projects/projet_test/').status_code == 404
    client.get('/admin')
    with client.session_transaction() as session:
        token = session['admin_csrf']
    response = client.post('/admin', data={'csrf_token': token, 'password': 'wrong'})
    assert 'Identifiant ou mot de passe incorrect' in response.get_data(as_text=True)
    assert client.get('/projects/projet_test/').status_code == 404


def test_development_requires_admin_for_drafts(client, app):
    app.config['ENV'] = 'development'
    assert client.get('/projects/projet_test/').status_code == 404
    assert all(card['published'] for card in client.get('/data/cartes').json)
    assert login(client, app).status_code == 302
    assert client.get('/projects/projet_test/').status_code == 200


def test_username_is_required_and_navigation_tracks_login(client, app):
    app.config['ADMIN_USERNAME'] = 'owner'
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('preview-password')
    assert 'Connexion' in client.get('/').get_data(as_text=True)
    html = client.get('/admin').get_data(as_text=True)
    assert 'autocomplete="username"' in html
    assert 'autocomplete="current-password"' in html
    for username in ('', 'wrong', 'échec'):
        with client.session_transaction() as session:
            token = session['admin_csrf']
        response = client.post('/admin', data={
            'csrf_token': token, 'username': username, 'password': 'preview-password',
        })
        assert 'Identifiant ou mot de passe incorrect' in response.get_data(as_text=True)
        assert client.get('/projects/projet_test/').status_code == 404
    assert login(client, app).status_code == 302
    assert 'Se déconnecter' in client.get('/').get_data(as_text=True)
    assert client.get('/admin').status_code == 302
    # The browser session never grants permission to persist shared data.
    assert client.post('/projects/todolist/api/todolist', json={'text': 'private'}).status_code == 403
    app.config['ADMIN_USERNAME'] = 'replacement'
    assert client.get('/projects/projet_test/').status_code == 404


def test_published_controls_both_project_lists(client, app):
    card = app.config['PROJECT_CARDS_BY_ID']['projet_test']
    for path in ('/lab', '/exploration'):
        assert card['titre'] not in client.get(path).get_data(as_text=True)
    login(client, app)
    for path in ('/lab', '/exploration'):
        assert card['titre'] in client.get(path).get_data(as_text=True)
    visitor = app.test_client()
    card['published'] = True
    assert visitor.get('/projects/projet_test/').status_code == 200
    assert card['titre'] in visitor.get('/lab').get_data(as_text=True)
    del card['published']
    assert visitor.get('/projects/projet_test/').status_code == 404
    assert card['titre'] not in visitor.get('/lab').get_data(as_text=True)
