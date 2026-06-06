from . import bp
from flask import render_template, jsonify, request
from .ai import minmax, get_valid_columns
import math
import json
import random
import time


@bp.get("/")
def home():
    return render_template("index_connect_four.html")

@bp.route("/api/ai-move", methods=["POST"])
def ai_move():
    data = request.get_json()

    grid = data["grid"]
    player = data["player"]
    ai_type = data.get("type", "easy")

    time.sleep(0.5)  # Simulate thinking time

    if ai_type == "easy":
        valid_columns = get_valid_columns(grid)
        column = random.choice(valid_columns) if valid_columns else None

    elif ai_type == "medium":
        column, score = minmax(
            grid, 
            depth=4, 
            alpha=-math.inf, 
            beta=math.inf, 
            maximizing=True, 
            ai_player=player
        )

    elif ai_type == "hard":
        column, score = minmax(
            grid, 
            depth=6, 
            alpha=-math.inf, 
            beta=math.inf, 
            maximizing=True, 
            ai_player=player
        )

    return jsonify({
        "column": column,
        "player": player,
        "type": ai_type
    })