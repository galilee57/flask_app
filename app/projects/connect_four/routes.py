from . import bp
from flask import render_template, jsonify, request
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

    if not grid or player not in [1, 2]:
        return jsonify({
            "column": None,
            "error": "Invalid input"
        }), 400

    available_columns = []

    for column in range(7):
        if grid[0][column] == 0:
            available_columns.append(column)

    if not available_columns:
        return jsonify({
            "column": None,
            "error": "No available columns"
        }), 400

    column = random.choice(available_columns)

    return jsonify({
        "column": column,
        "player": player,
        "type": ai_type
    })