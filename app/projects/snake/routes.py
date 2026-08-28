from . import bp
from flask import render_template, jsonify, request
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

    dx = DIRECTIONS[direction]["x"]
    dy = DIRECTIONS[direction]["y"]

    head = game.snake[0]

    new_head = {
        "x": head["x"] + dx,
        "y": head["y"] + dy,
    }

    # Collision avec les bords
    if (
        new_head["x"] < 0
        or new_head["x"] >= game.GRID_W
        or new_head["y"] < 0
        or new_head["y"] >= game.GRID_H
    ):
        game.game_over = True
        game.message = "GAME OVER : le serpent est sorti du plateau !"
        return jsonify(game.to_dict())

    # Collision avec le corps
    if new_head in game.snake:
        game.game_over = True
        game.message = "GAME OVER : le serpent s'est mordu !"
        return jsonify(game.to_dict())

    game.direction = direction
    game.snake.insert(0, new_head)
    game.steps_since_fruit += 1
    game.total_steps += 1

    if new_head == game.fruit:
        game.score += 1
        print("Fruit mangé")

        if record:
            stat = SnakeStat(
                mode=mode,
                score=game.score,
                steps_since_fruit=game.steps_since_fruit,
                total_steps=game.total_steps,
            )

            db.session.add(stat)
            db.session.commit()

        game.steps_since_fruit = 0
        game.fruit = game.generate_fruit()
    else:
        game.snake.pop()

    return jsonify(game.to_dict())


@bp.post("/api/reset")
def reset_game():
    game.reset()
    return jsonify(game.to_dict())


@bp.get("/api/astar")
def get_astar_path():
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
