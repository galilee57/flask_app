import click

from . import bp
from flask import render_template, jsonify, request, current_app, session
from werkzeug.local import LocalProxy
from .snake_game import Game
from .algorithms import astar, path_to_direction
from app.extensions import db
from .models import SnakeStat, SnakeResult
from app.core.security import enforce_admin_api_token
from sqlalchemy import func

DIRECTIONS = {
    "up": {"x": 0, "y": -1},
    "down": {"x": 0, "y": 1},
    "left": {"x": -1, "y": 0},
    "right": {"x": 1, "y": 0},
}

def _get_game():
    if "portfolio.snake" not in request.environ:
        instance = Game()
        stored = session.get("snake_game")
        if stored:
            for key in ("fruit", "snake", "direction", "score", "game_over",
                        "steps_since_fruit", "total_steps", "message", "game_id", "mode"):
                if key in stored:
                    setattr(instance, key, stored[key])
        request.environ["portfolio.snake"] = instance
    return request.environ["portfolio.snake"]


game = LocalProxy(_get_game)


@bp.after_request
def save_game(response):
    if "portfolio.snake" in request.environ and response.status_code < 400:
        session["snake_game"] = request.environ["portfolio.snake"].to_dict()
    return response


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

    mode = "human" if mode == "manual" else mode
    if mode not in ("human", "astar", "astar_nn"):
        return jsonify(error="Mode invalide."), 400
    if game.mode is not None and game.mode != mode:
        return jsonify(error="Réinitialise la partie pour changer de mode."), 409
    game.mode = mode
    game.step(direction)
    if not game.game_over and game.steps_since_fruit >= 100 * len(game.snake):
        game.game_over = True
        game.message = "Partie terminée : trop de déplacements sans fruit."

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
    if game.mode not in (None, "astar"):
        return jsonify(error="Réinitialise la partie pour changer de mode."), 409
    record = request.args.get("record", "false").lower() == "true"
    if record:
        enforce_admin_api_token()

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
        game.mode = "astar"
        game.game_over = True
        game.message = "Partie terminée : aucun chemin vers le fruit."
        return jsonify(game.to_dict())

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
    from pathlib import Path
    path = Path(current_app.config.get("SNAKE_DQN_PATH") or Path(current_app.instance_path) / "snake_dqn.npz")
    train(episodes, seed, path, report=click.echo)
    click.echo(f"Modèle enregistré : {path}")


@bp.get("/api/results")
def results():
    rows = SnakeResult.query.order_by(SnakeResult.created_at.desc()).limit(100).all()
    return jsonify([row.to_dict() for row in rows])


@bp.post("/api/results")
def record_result():
    enforce_admin_api_token()
    if not game.game_over or game.mode != "human":
        return jsonify(error="Seule une partie humaine terminée peut être enregistrée."), 409
    # A stale browser response must not record a different game after a reset.
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Corps JSON invalide."), 400
    if payload.get("game_id") != game.game_id:
        return jsonify(error="Cette partie n'est plus active."), 409
    row = db.session.get(SnakeResult, game.game_id)
    if row is None:
        row = SnakeResult(id=game.game_id, mode="human", score=game.score,
                          total_steps=game.total_steps,
                          end_reason=("board_full" if game.fruit is None else
                                      "no_progress" if game.steps_since_fruit >= 100 * len(game.snake)
                                      else "collision"))
        db.session.add(row)
        db.session.commit()
    return jsonify(row.to_dict())


@bp.cli.command("snake-benchmark")
@click.option("--seed", default=42, type=int)
@click.option("--max-steps", default=10000, type=click.IntRange(1, 100000))
@click.option("--dry-run", is_flag=True)
def benchmark_snake(seed, max_steps, dry_run):
    """Simulate one A* and one trained DQN game, then persist both atomically."""
    from .benchmark import simulate_references
    from .rl import checkpoint_path
    try:
        rows = simulate_references(checkpoint_path(current_app), seed, max_steps)
    except (OSError, ValueError, KeyError) as exc:
        raise click.ClickException("Modèle DQN absent ou invalide ; aucun résultat enregistré.") from exc
    for row in rows:
        click.echo(f"{row.mode}: score={row.score}, cases={row.total_steps}, fin={row.end_reason}")
        if not dry_run and db.session.get(SnakeResult, row.id) is None:
            db.session.add(row)
    if not dry_run:
        db.session.commit()
    click.echo("Simulation sans écriture." if dry_run else "Résultats enregistrés (sans doublons).")
