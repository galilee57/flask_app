"""Bounded, reproducible reference games with no database access during play."""
import hashlib
import random

from .algorithms import astar, path_to_direction
from .models import SnakeResult
from .rl import DQN, action_direction, encode_state
from .snake_game import Game


def simulate_references(model_path, seed=42, max_steps=10000):
    model = DQN.load(model_path)
    fingerprint = hashlib.sha256(model_path.read_bytes()).hexdigest()
    results = []
    for mode in ("astar", "astar_nn"):
        game = Game(random.Random(seed))
        reason = "step_limit"
        for _ in range(max_steps):
            if mode == "astar":
                path = astar(game.snake[0], game.fruit, game.GRID_W,
                             game.GRID_H, game.snake[1:])
                direction = path_to_direction(path)
                if direction is None:
                    reason = "no_path"
                    break
            else:
                action = int(model.predict(encode_state(game))[0].argmax())
                direction = action_direction(game.direction, action)
            game.step(direction)
            if game.game_over:
                reason = "board_full" if game.fruit is None else "collision"
                break
            if game.steps_since_fruit >= 100 * len(game.snake):
                reason = "no_progress"
                break
        model_hash = fingerprint if mode == "astar_nn" else None
        identity = f"snake-reference-v1:{mode}:{seed}:{max_steps}:{model_hash}"
        results.append(SnakeResult(
            id=hashlib.sha256(identity.encode()).hexdigest(), mode=mode,
            score=game.score, total_steps=game.total_steps, end_reason=reason,
            seed=seed, model_hash=model_hash))
    return results
