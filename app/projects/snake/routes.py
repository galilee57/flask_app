import click

from . import bp
from flask import render_template, jsonify, request, current_app
from .snake_game import Game
from .algorithms import astar, path_to_direction
from app.extensions import db
from .models import SnakeStat
from app.security import enforce_admin_api_token
from sqlalchemy import func

DIRECTIONS = {
    "up": {"x": 0, "y": -1},
    "down": {"x": 0, "y": 1},
    "left": {"x": -1, "y": 0},
    "right": {"x": 1, "y": 0},
}

game = Game()


@bp.get("/")
def home():
    return render_template("index_snake.html")


@bp.get("/api/state")
def get_state():
    return jsonify(game.to_dict())


@bp.post("/api/move/<direction>/<mode>")
def move_snake(direction, mode, record=None):
    if record is None:
        record = request.args.get("record", "false").lower() == "true"
    if record:
        enforce_admin_api_token()

    if game.game_over:
        return jsonify(game.to_dict())

    if direction not in DIRECTIONS:
        return jsonify({"error": "Direction invalide"}), 400

    previous_score = game.score
    steps_to_fruit = game.steps_since_fruit + 1
    game.step(direction)
    if record and game.score > previous_score:
        db.session.add(SnakeStat(
            mode=mode, score=game.score,
            steps_since_fruit=steps_to_fruit, total_steps=game.total_steps,
        ))
        db.session.commit()

    return jsonify(game.to_dict())


@bp.post("/api/reset")
def reset_game():
    game.reset()
    return jsonify(game.to_dict())


@bp.get("/api/astar")
def get_astar_path():
    if game.game_over:
        return jsonify({"path": []})

    path = astar(
        start=game.snake[0],
        goal=game.fruit,
        grid_w=game.GRID_W,
        grid_h=game.GRID_H,
        obstacles=game.snake[1:],
    )

    if not path:
        return jsonify({"path": []})

    return jsonify({
        "path": [{"x": x, "y": y} for x, y in path]
    })


@bp.post("/api/ai/move")
def ai_move():
    record = request.args.get("record", "false").lower() == "true"

    if game.game_over:
        return jsonify(game.to_dict())

    path = astar(
        start=game.snake[0],
        goal=game.fruit,
        grid_w=game.GRID_W,
        grid_h=game.GRID_H,
        obstacles=game.snake[1:],
    )

    if not path:
        return jsonify({"error": "Aucun chemin trouvé"}), 400

    direction = path_to_direction(path)

    if direction is None:
        return jsonify({"error": "Direction impossible à déterminer"}), 400

    return move_snake(direction, "astar", record)


@bp.get("/api/stats")
def get_stats():
    stats = SnakeStat.query.order_by(SnakeStat.created_at.asc()).all()

    return jsonify([
        {
            "mode": stat.mode,
            "score": stat.score,
            "steps_since_fruit": stat.steps_since_fruit,
            "total_steps": stat.total_steps,
            "created_at": stat.created_at.isoformat(),
        }
        for stat in stats
    ])

@bp.get("/api/stats/curve")
def get_stats_curve():
    rows = (
        db.session.query(
            SnakeStat.mode,
            SnakeStat.score,
            func.avg(SnakeStat.total_steps).label("avg_steps")
        )
        .group_by(SnakeStat.mode, SnakeStat.score)
        .order_by(SnakeStat.mode.asc(), SnakeStat.score.asc())
        .all()
    )

    return jsonify([
        {
        "mode": row.mode,
        "score": row.score,
        "avg_steps": round(row.avg_steps, 2)
        }
        for row in rows
    ])


@bp.post("/api/rl/move")
def rl_move():
    record = request.args.get("record", "false").lower() == "true"
    if record:
        enforce_admin_api_token()
    if game.game_over:
        return jsonify(game.to_dict())
    from .rl import DQN, encode_state, action_direction, checkpoint_path
    path = checkpoint_path(current_app)
    if not path.is_file():
        return jsonify({"error": "Entraîne le réseau avec la commande snake-train avant de jouer."}), 409
    cached = current_app.extensions.get("snake_dqn")
    stamp = path.stat().st_mtime_ns
    if cached is None or cached[0] != str(path) or cached[1] != stamp:
        try:
            cached = (str(path), stamp, DQN.load(path))
        except (ValueError, KeyError, OSError):
            return jsonify({"error": "Le modèle DQN est invalide."}), 503
        current_app.extensions["snake_dqn"] = cached
    action = int(cached[2].predict(encode_state(game))[0].argmax())
    return move_snake(action_direction(game.direction, action), "astar_nn", record)


@bp.cli.command("snake-train")
@click.option("--episodes", default=1000, type=click.IntRange(min=1))
@click.option("--seed", default=42, type=int)
def train_snake(episodes, seed):
    """Train a DQN in independent games and save it in the instance folder."""
    from .rl import train, checkpoint_path
    path = checkpoint_path(current_app)
    train(episodes, seed, path, report=click.echo)
    click.echo(f"Modèle enregistré : {path}")
