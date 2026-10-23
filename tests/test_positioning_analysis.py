import copy
import json
import time
from hashlib import sha256

import pytest
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.projects.professional_positioning.analysis import import_analysis, run_view, validate_analysis
from app.projects.professional_positioning.models import AnalysisRun, MemoryEntry, Profile, ReviewObservation, WorkItem

BASE = '/projects/professional_positioning'


def payload():
    def bi(value):
        return {'fr': value, 'en': value}
    source = {'key': 's1', 'url': 'https://example.org/project', 'excerpt': 'Documented API',
              'consulted_at': '2026-01-01T12:00:00Z', 'method': 'web_open', 'kind': 'self_report'}
    return {'schema_version': 2, 'import_key': 'initial', 'actor': 'Codex research',
            'title': 'Private analysis', 'context': 'Manual corpus',
            'rubric': [{'key': 'api', 'label': bi('API'), 'definition': bi('API integration')}],
            'summary': [bi('Private findings')], 'limitations': [bi('Not a market sample')],
            'reviews': [
                {'name': name, 'kind': kind, 'origin_url': origin, 'role_label': 'Solutions Engineer',
                 'comparability': tier, 'scope': 'Homepage and projects', 'sources': [copy.deepcopy(source)],
                 'observations': [{'criterion': 'api', 'status': 'claimed', 'finding': bi('Describes API'),
                                   'confidence': 'medium', 'confidence_reason': bi('Author statement'), 'source_keys': ['s1']}]}
                for name, kind, origin, tier in [('Me', 'portfolio', 'https://target.example/', 'target'),
                                                 ('Reference', 'reference', 'https://reference.example/', 'exact')]],
            'actions': [{'criterion': 'api', 'title': 'Add API artifact', 'body': 'Document a real integration', 'priority': 'high'}]}


def login(client, app):
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('preview')
    with client.session_transaction() as session:
        session.update(admin_until=time.time()+3600, admin_username=app.config['ADMIN_USERNAME'],
                       admin_hash=sha256(app.config['ADMIN_PASSWORD_HASH'].encode()).hexdigest())


def test_append_preserves_runs_sources_and_manual_work(app):
    with app.app_context():
        initial = payload()
        first, created = import_analysis(initial)
        db.session.commit()
        assert created
        assert import_analysis(initial)[0].id == first.id
        bad = copy.deepcopy(initial)
        bad['summary'][0]['en'] = 'changed'
        with pytest.raises(ValueError, match='import_key_conflict'):
            import_analysis(bad)
        action = db.session.scalar(db.select(WorkItem))
        action.status = 'in_progress'
        entry = MemoryEntry(id='note', diagnostic_id=first.diagnostic_id, run_id=first.id,
                            kind='comment', body='New evidence available', actor='user')
        db.session.add(entry)
        db.session.commit()
        amendment = copy.deepcopy(initial)
        amendment['import_key'] = 'amendment'
        amendment['memory_entry_ids'] = ['note']
        amendment['reviews'][0]['sources'][0]['kind'] = 'artifact'
        amendment['reviews'][0]['observations'][0]['status'] = 'demonstrated'
        with pytest.raises(ValueError, match='parent_required'):
            import_analysis(amendment, first.diagnostic_id)
        second, _ = import_analysis(amendment, first.diagnostic_id, first.id)
        db.session.commit()
        assert second.parent_id == first.id
        assert second.memory_entry_ids == ['note']
        assert run_view(first)['target']['observations']['api'].status == 'claimed'
        assert run_view(second)['target']['observations']['api'].status == 'demonstrated'
        assert db.session.scalar(db.select(db.func.count()).select_from(Profile)) == 2
        assert db.session.scalar(db.select(db.func.count()).select_from(WorkItem)) == 1
        assert db.session.get(WorkItem, action.id).status == 'in_progress'
        assert run_view(second)['comparison'][0]['count'] == 1
        amendment['import_key'] = 'stale-parent'
        with pytest.raises(ValueError, match='parent_must_be_latest'):
            import_analysis(amendment, first.diagnostic_id, first.id)


@pytest.mark.parametrize('change', ['missing_source', 'future_date', 'fake_artifact', 'duplicate_origin', 'missing_observation'])
def test_invalid_evidence_is_rejected(change):
    data = payload()
    review = data['reviews'][1]
    if change == 'missing_source':
        review['observations'][0]['source_keys'] = ['invented']
    elif change == 'future_date':
        review['sources'][0]['consulted_at'] = '2099-01-01T00:00:00Z'
    elif change == 'fake_artifact':
        review['observations'][0]['status'] = 'demonstrated'
    elif change == 'duplicate_origin':
        review['origin_url'] = data['reviews'][0]['origin_url']
    else:
        review['observations'] = []
    with pytest.raises(ValueError):
        validate_analysis(data)


def test_dashboard_comments_evidence_and_action_audit(client, app, admin_headers):
    with app.app_context():
        run, _ = import_analysis(payload())
        db.session.commit()
        identifier, rid = run.diagnostic_id, run.id
        aid = db.session.scalar(db.select(WorkItem.id))
    dashboard = f'{BASE}/diagnostics/{identifier}/dashboard'
    assert client.get(dashboard).status_code == 404
    assert client.get(f'{BASE}/api/diagnostics/{identifier}/context').status_code == 404
    login(client, app)
    assert client.get(BASE + '/').status_code == 302
    for lang in ('fr', 'en'):
        response = client.get(dashboard + '?lang=' + lang)
        assert response.status_code == 200
        assert b'https://reference.example/' in response.data
        assert response.headers['Cache-Control'] == 'private, no-store'
    memory = f'{BASE}/api/diagnostics/{identifier}/memory'
    note = {'kind': 'comment', 'run_id': rid, 'criterion': 'api', 'body': '<script>private</script>'}
    assert client.post(memory, json=note).status_code == 403
    assert client.post(memory, json=note, headers=admin_headers).status_code == 201
    evidence = {**note, 'kind': 'evidence', 'url': 'https://private.example/proof', 'excerpt': 'My proof', 'consulted_at': '2026-01-01T00:00:00Z'}
    assert client.post(memory, json=evidence, headers=admin_headers).status_code == 201
    assert client.post(memory, json={**evidence, 'url':'javascript:alert(1)'}, headers=admin_headers).status_code == 400
    assert client.post(f'{BASE}/api/actions/{aid}/status', json={'status':'done'}, headers=admin_headers).status_code == 200
    context = client.get(f'{BASE}/api/diagnostics/{identifier}/context').json
    assert context['actions'][0]['status'] == 'done'
    assert context['memory'][-1]['kind'] == 'status_change'
    assert context['memory'][1]['evidence']['verification'] == 'pending_review'
    assert len(context['runs'][0]['reviews'][1]['sources']) == 1
    assert b'&lt;script&gt;private&lt;/script&gt;' in client.get(dashboard).data
    anonymous = app.test_client()
    assert anonymous.get(dashboard).status_code == 404
    assert anonymous.post(memory, json=note, headers=admin_headers).status_code == 404
    with app.app_context():
        assert db.session.scalar(db.select(ReviewObservation).limit(1)).status == 'claimed'


def test_cli_validation_and_protected_atomic_import(app, tmp_path):
    path = tmp_path / 'analysis.json'
    path.write_text(json.dumps(payload()))
    runner = app.test_cli_runner()
    assert runner.invoke(args=['positioning-import', str(path)]).exit_code == 0
    assert runner.invoke(args=['positioning-import', str(path), '--apply']).exit_code != 0
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(AnalysisRun)) == 0
    result = runner.invoke(args=['positioning-import', str(path), '--apply', '--admin-token', 'test-admin-token'])
    assert result.exit_code == 0, result.output
    with app.app_context():
        identifier = db.session.scalar(db.select(AnalysisRun.diagnostic_id))
    result = runner.invoke(args=['positioning-context', identifier, '--output', str(tmp_path/'public.json')])
    assert result.exit_code != 0
