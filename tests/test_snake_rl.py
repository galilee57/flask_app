import numpy as np

from app.projects.snake.snake_game import Game
from app.projects.snake.rl import DQN, encode_state, action_direction, train


def test_relative_actions_and_collision():
    game = Game()
    assert [action_direction('right', a) for a in range(3)] == ['right', 'down', 'up']
    assert encode_state(game).shape == (11,)
    before = list(game.snake)
    reward, done = game.step('left')
    assert done and reward == -10
    assert game.snake == before


def test_fruit_reward_and_full_board():
    game = Game()
    game.fruit = {'x': 6, 'y': 5}
    assert game.step('right') == (10, False)
    assert len(game.snake) == 4 and game.score == 1
    game.GRID_W = 4
    game.GRID_H = 1
    game.snake = [{'x': 2, 'y': 0}, {'x': 1, 'y': 0}, {'x': 0, 'y': 0}]
    game.fruit = {'x': 3, 'y': 0}
    assert game.step('right') == (10, True)
    assert game.fruit is None


def test_terminal_update_and_roundtrip(tmp_path):
    model, target = DQN(), DQN()
    state = np.ones(11, dtype=np.float32)
    before = model.predict(state)[0, 0]
    batch = [(state, 0, -10.0, state, True)] * 64
    loss = model.update(batch, target)
    assert np.isfinite(loss)
    assert model.predict(state)[0, 0] < before
    path = tmp_path / 'model.npz'
    model.save(path)
    np.testing.assert_array_equal(model.predict(state), DQN.load(path).predict(state))


def test_training_saves_loadable_model(tmp_path):
    path = tmp_path / 'trained.npz'
    train(3, 42, path, report=lambda message: None)
    assert np.isfinite(DQN.load(path).predict(encode_state(Game()))).all()


def test_rl_missing_model_and_security(client, admin_headers, tmp_path):
    client.application.config['SNAKE_DQN_PATH'] = str(tmp_path / 'model.npz')
    client.post("/projects/snake/api/reset")
    assert client.post('/projects/snake/api/rl/move').status_code == 409
    DQN().save(tmp_path / 'model.npz')
    before = client.get("/projects/snake/api/state").get_json()
    assert client.post('/projects/snake/api/rl/move?record=true').status_code == 403
    assert client.get("/projects/snake/api/state").get_json() == before
    assert client.post('/projects/snake/api/rl/move', headers=admin_headers).status_code == 200
