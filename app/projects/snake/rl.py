"""Small NumPy DQN with replay memory and a periodically synchronized target."""
from collections import deque
from pathlib import Path
import os
import random
import tempfile

import numpy as np

from .snake_game import Game

DIRECTIONS = ("up", "right", "down", "left")
GAMMA = 0.99


def fruit_potential(game):
    if game.game_over or game.fruit is None:
        return 0.0
    head, fruit = game.snake[0], game.fruit
    return -0.1 * (abs(head["x"] - fruit["x"]) + abs(head["y"] - fruit["y"]))


def shaped_reward(reward, before, game):
    # Potential shaping includes the NEW fruit after eating and zero at termination.
    return reward + GAMMA * fruit_potential(game) - before


def action_direction(direction, action):
    # 0: straight, 1: clockwise, 2: counterclockwise.
    return DIRECTIONS[(DIRECTIONS.index(direction) + (0, 1, -1)[action]) % 4]


def encode_state(game):
    head = game.snake[0]
    fruit = game.fruit or head
    return np.asarray([
        *[game.danger(action_direction(game.direction, a)) for a in range(3)],
        *[game.direction == d for d in DIRECTIONS],
        fruit["x"] < head["x"], fruit["x"] > head["x"],
        fruit["y"] < head["y"], fruit["y"] > head["y"],
    ], dtype=np.float32)


def checkpoint_path(app):
    return Path(app.config.get("SNAKE_DQN_PATH", Path(app.instance_path) / "snake_dqn.npz"))


class DQN:
    def __init__(self, seed=42):
        rng = np.random.default_rng(seed)
        self.w1 = (rng.standard_normal((11, 128)) * np.sqrt(2 / 11)).astype(np.float32)
        self.b1 = np.zeros(128, dtype=np.float32)
        self.w2 = (rng.standard_normal((128, 3)) * np.sqrt(2 / 128)).astype(np.float32)
        self.b2 = np.zeros(3, dtype=np.float32)
        self.optimizer_steps = 0
        self.moments = {name: (np.zeros_like(getattr(self, name)),
                               np.zeros_like(getattr(self, name)))
                        for name in ("w1", "b1", "w2", "b2")}

    def predict(self, states):
        states = np.atleast_2d(states)
        return np.maximum(states @ self.w1 + self.b1, 0) @ self.w2 + self.b2

    def copy_from(self, other):
        for name in ("w1", "b1", "w2", "b2"):
            setattr(self, name, getattr(other, name).copy())

    def update(self, batch, target, gamma=GAMMA, learning_rate=0.0003):
        states, actions, rewards, next_states, dones = zip(*batch)
        states = np.asarray(states)
        hidden_pre = states @ self.w1 + self.b1
        hidden = np.maximum(hidden_pre, 0)
        q = hidden @ self.w2 + self.b2
        rows = np.arange(len(batch))
        # Double DQN: online network selects, target network evaluates.
        next_actions = self.predict(next_states).argmax(axis=1)
        next_q = target.predict(next_states)[rows, next_actions]
        expected = np.asarray(rewards) + gamma * (1 - np.asarray(dones)) * next_q
        errors = q[rows, actions] - expected
        # Huber loss derivative and global clipping keep early updates bounded.
        dq = np.zeros_like(q)
        dq[rows, actions] = np.clip(errors, -1, 1) / len(batch)
        dh = (dq @ self.w2.T) * (hidden_pre > 0)
        grads = (states.T @ dh, dh.sum(axis=0), hidden.T @ dq, dq.sum(axis=0))
        norm = np.sqrt(sum(float(np.sum(g * g)) for g in grads))
        scale = min(1.0, 10.0 / max(norm, 1e-8))
        self.optimizer_steps += 1
        for name, grad in zip(("w1", "b1", "w2", "b2"), grads):
            grad = grad * scale
            first, second = self.moments[name]
            first[:] = 0.9 * first + 0.1 * grad
            second[:] = 0.999 * second + 0.001 * grad**2
            corrected_first = first / (1 - 0.9**self.optimizer_steps)
            corrected_second = second / (1 - 0.999**self.optimizer_steps)
            getattr(self, name)[:] -= learning_rate * corrected_first / (np.sqrt(corrected_second) + 1e-8)
        return float(np.mean(np.where(np.abs(errors) <= 1, 0.5 * errors**2, np.abs(errors) - 0.5)))

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement prevents web workers from reading a partial model.
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as handle:
            temporary = handle.name
            np.savez(handle, version=np.asarray(1), **{
                name: getattr(self, name) for name in ("w1", "b1", "w2", "b2")
            })
        try:
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @classmethod
    def load(cls, path):
        model = cls()
        with np.load(path, allow_pickle=False) as data:
            if data["version"].item() != 1:
                raise ValueError("Unsupported model version")
            for name in ("w1", "b1", "w2", "b2"):
                array = data[name]
                if array.shape != getattr(model, name).shape or not np.isfinite(array).all():
                    raise ValueError("Invalid model weights")
                setattr(model, name, array.astype(np.float32))
        return model


def train(episodes, seed, path, report=print):
    # Restore global randomness so training cannot change a running game's RNG.
    previous_rng = random.getstate()
    random.seed(seed)
    rng = random.Random(seed)
    online, target = DQN(seed), DQN(seed)
    target.copy_from(online)
    memory = deque(maxlen=10000)
    updates = 0
    scores = deque(maxlen=100)
    try:
        for episode in range(episodes):
            game = Game()
            epsilon = max(0.05, 1.0 - episode / max(1, episodes * 0.8))
            while not game.game_over:
                state = encode_state(game)
                action = rng.randrange(3) if rng.random() < epsilon else int(online.predict(state)[0].argmax())
                potential = fruit_potential(game)
                reward, done = game.step(action_direction(game.direction, action))
                # No-fruit cutoff is an explicit terminal rule of the training task.
                if not done and game.steps_since_fruit >= 100 * len(game.snake):
                    game.game_over = done = True
                    reward = -10.0
                reward = shaped_reward(reward, potential, game)
                memory.append((state, action, reward, encode_state(game), done))
                if len(memory) >= 64:
                    online.update(rng.sample(list(memory), 64), target)
                    updates += 1
                    if updates % 250 == 0:
                        target.copy_from(online)
            scores.append(game.score)
            if (episode + 1) % 100 == 0 or episode + 1 == episodes:
                report(f"Partie {episode + 1}/{episodes} | score moyen : {np.mean(scores):.2f} | epsilon : {epsilon:.2f}")
        online.save(path)
    finally:
        random.setstate(previous_rng)
