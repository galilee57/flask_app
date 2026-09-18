from app.extensions import db
from app.projects.snake.models import SnakeResult, SnakeStat
from app.projects.snake.snake_game import Game
from app.projects.snake.benchmark import simulate_references
from app.projects.snake.rl import DQN


def test_only_finished_human_game_is_saved_once(client, admin_headers):
    state = Game()
    state.fruit = {"x": 6, "y": 5}
    with client.session_transaction() as session:
        session["snake_game"] = state.to_dict()
    response = client.post('/projects/snake/api/move/right/human?record=true', headers=admin_headers)
    assert response.get_json()['score'] == 1
    assert SnakeStat.query.count() == SnakeResult.query.count() == 0
    payload = {'game_id': state.game_id, 'score': 9999}
    assert client.post('/projects/snake/api/results', json=payload, headers=admin_headers).status_code == 409
    end = client.post('/projects/snake/api/move/left/human').get_json()
    assert end['game_over']
    assert client.post('/projects/snake/api/results', json=payload).status_code == 403
    for _ in range(2):
        response = client.post('/projects/snake/api/results', json=payload, headers=admin_headers)
        assert response.status_code == 200
        assert response.get_json()['score'] == 1
    assert SnakeResult.query.count() == 1
    client.post('/projects/snake/api/reset')
    assert client.post('/projects/snake/api/results', json=payload, headers=admin_headers).status_code == 409


def test_ai_cannot_be_recorded_or_switched_to_human(client, admin_headers):
    client.post('/projects/snake/api/ai/move')
    assert client.post('/projects/snake/api/move/right/human').status_code == 409
    with client.session_transaction() as session:
        state = session['snake_game']
        state['game_over'] = True
        session['snake_game'] = state
    assert client.post('/projects/snake/api/results', json={'game_id': state['game_id']},
                       headers=admin_headers).status_code == 409
    assert SnakeResult.query.count() == 0


def test_references_reproducible_and_cli_idempotent(app, tmp_path):
    path = tmp_path / 'dqn.npz'
    DQN().save(path)
    first = simulate_references(path, seed=42, max_steps=20)
    second = simulate_references(path, seed=42, max_steps=20)
    assert [(r.id, r.score, r.total_steps, r.end_reason) for r in first] == [
        (r.id, r.score, r.total_steps, r.end_reason) for r in second]
    assert [r.mode for r in first] == ['astar', 'astar_nn']
    app.config['SNAKE_DQN_PATH'] = str(path)
    runner = app.test_cli_runner()
    args = ['snake', 'snake-benchmark', '--max-steps', '20']
    assert runner.invoke(args=args + ['--dry-run']).exit_code == 0
    assert SnakeResult.query.count() == 0
    for _ in range(2):
        result = runner.invoke(args=args)
        assert result.exit_code == 0, result.output
    assert SnakeResult.query.count() == 2
    app.config['SNAKE_DQN_PATH'] = str(tmp_path / 'missing.npz')
    assert runner.invoke(args=args).exit_code != 0
    assert SnakeResult.query.count() == 2


def test_results_exclude_legacy_fruit_stats(client):
    db.session.add(SnakeStat(mode='human', score=5, total_steps=25, steps_since_fruit=5))
    db.session.commit()
    assert client.get('/projects/snake/api/results').get_json() == []
