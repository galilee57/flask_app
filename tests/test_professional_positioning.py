import time

from werkzeug.security import generate_password_hash
from app.extensions import db
from app.projects.professional_positioning.models import Assessment, PublicSnapshot

BASE = '/projects/professional_positioning'


def login(client, app):
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('test-password')
    client.get('/admin')
    with client.session_transaction() as session:
        csrf = session['admin_csrf']
    client.post('/admin', data={'csrf_token': csrf, 'username': app.config['ADMIN_USERNAME'], 'password': 'test-password'})


def create(client, headers):
    response = client.post(BASE + '/api/diagnostics', json={'title': 'PRIVATE TITLE', 'role': 'agentic_ai', 'context': 'PRIVATE CONTEXT'}, headers=headers)
    assert response.status_code == 201
    return response.json['url'].split('/')[-1]


def test_private_access_independent_of_catalogue(client, app, admin_headers):
    app.config['PROJECT_CARDS_BY_ID']['professional_positioning']['published'] = True
    assert client.get(BASE + '/').status_code == 404
    assert client.post(BASE + '/api/diagnostics', json={}, headers=admin_headers).status_code == 404
    login(client, app)
    response = client.get(BASE + '/')
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'private, no-store'
    assert client.post(BASE + '/api/diagnostics', json={}).status_code == 403
    with client.session_transaction() as session:
        session['admin_until'] = time.time() - 1
    assert client.get(BASE + '/').status_code == 404


def test_evidence_snapshot_lifecycle_and_no_source_disclosure(client, app, admin_headers):
    login(client, app)
    identifier = create(client, admin_headers)
    assert client.post(f'{BASE}/api/diagnostics/{identifier}/snapshots', headers=admin_headers).status_code == 400
    for i in range(5):
        profile = client.post(f'{BASE}/api/diagnostics/{identifier}/profiles', json={'name': f'SECRET PERSON {i}', 'url': f'https://private.example/{i}', 'kind': 'reference', 'rationale': 'SECRET RATIONALE'}, headers=admin_headers).json['id']
        payload = {'profile_id': profile, 'criterion': 'tools', 'finding': 'SECRET FINDING', 'confidence': 'high', 'confidence_reason': 'SECRET REASON', 'url': 'https://private.example/proof', 'excerpt': '<script>SECRET EXCERPT</script>', 'consulted_at': '2026-01-01T10:00:00Z'}
        assert client.post(f'{BASE}/api/diagnostics/{identifier}/assessments', json={**payload, 'consulted_at': '2099-01-01T00:00:00Z'}, headers=admin_headers).status_code == 400
        result = client.post(f'{BASE}/api/diagnostics/{identifier}/assessments', json=payload, headers=admin_headers)
        assert result.status_code == 201
        assessment_id = result.json['id']
        if i == 4:
            assert client.post(f'{BASE}/api/diagnostics/{identifier}/snapshots', headers=admin_headers).status_code == 400
        assert client.post(f'{BASE}/api/assessments/{assessment_id}/verify', headers=admin_headers).status_code == 200
    report = client.get(f'{BASE}/diagnostics/{identifier}?lang=en')
    assert report.status_code == 200
    assert b'&lt;script&gt;SECRET' in report.data
    assert b'Undocumented' in report.data
    snapshot = client.post(f'{BASE}/api/diagnostics/{identifier}/snapshots', headers=admin_headers)
    assert snapshot.status_code == 201
    sid = snapshot.json['url'].split('/')[-1]
    assert client.get('/positioning/' + sid).status_code == 404
    assert client.get(snapshot.json['url']).status_code == 200
    public_url = client.post(f'{BASE}/api/snapshots/{sid}/publish', headers=admin_headers).json['url']
    anonymous = app.test_client()
    for lang in ('en', 'fr'):
        public = anonymous.get(public_url + '?lang=' + lang)
        assert public.status_code == 200
        for secret in (b'SECRET', b'private.example', b'PRIVATE TITLE', b'PRIVATE CONTEXT', identifier.encode(), assessment_id.encode()):
            assert secret not in public.data
    with app.app_context():
        frozen = db.session.get(PublicSnapshot, sid).payload
        assert frozen['rows'][0]['count'] == 5
        assert frozen['rows'][1]['count'] is None
        proof = db.session.get(Assessment, assessment_id)
        proof.verified_at = None
        db.session.commit()
        assert db.session.get(PublicSnapshot, sid).payload == frozen
    assert anonymous.get(f'{BASE}/snapshots/{sid}').status_code == 404
    provenance_url = f'{BASE}/api/snapshots/{sid}/provenance'
    assert anonymous.get(provenance_url).status_code == 404
    assert client.get(provenance_url).json['assessments'][0]['excerpt'] == '<script>SECRET EXCERPT</script>'
    assert client.post(f'{BASE}/api/snapshots/{sid}/withdraw', headers=admin_headers).status_code == 200
    assert anonymous.get(public_url).status_code == 404


def test_languages_roles_validation_and_edit_invalidates_verification(client, app, admin_headers):
    login(client, app)
    for lang in ('fr', 'en'):
        assert client.get(BASE + '/?lang=' + lang).status_code == 200
    assert client.post(BASE + '/api/diagnostics', json={'title':'x','context':'y','role':'invented'}, headers=admin_headers).status_code == 400
    identifier = create(client, admin_headers)
    assert client.post(f'{BASE}/api/diagnostics/{identifier}/profiles', json={'name':'x','kind':'portfolio','rationale':'x','url':'javascript:alert(1)'}, headers=admin_headers).status_code == 400
    profile = client.post(f'{BASE}/api/diagnostics/{identifier}/profiles', json={'name':'x','kind':'portfolio','rationale':'x','url':'https://example.com'}, headers=admin_headers).json['id']
    payload = dict(profile_id=profile, criterion='tools', finding='observed', confidence='low', confidence_reason='self reported', url='https://example.com', excerpt='tools', consulted_at='2026-01-01T00:00:00Z')
    route = f'{BASE}/api/diagnostics/{identifier}/assessments'
    aid = client.post(route, json=payload, headers=admin_headers).json['id']
    client.post(f'{BASE}/api/assessments/{aid}/verify', headers=admin_headers)
    assert client.post(route, json=payload, headers=admin_headers).json['id'] == aid
    with app.app_context():
        assert db.session.get(Assessment, aid).verified_at is None
