from . import bp
from flask import render_template, jsonify, request
from .solver import astar_with_tree
import json


@bp.get("/")
def home():
    return render_template("index_a_star.html")

@bp.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    start = tuple(data["state"])

    result = astar_with_tree(start)

    return jsonify({
        "solvable": len(result["solution"]) > 0,
        "solution": result["solution"],
        "moves": max(0, len(result["solution"]) - 1),
        "tree_nodes": result["tree_nodes"]
    })