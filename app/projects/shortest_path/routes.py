from flask import jsonify, render_template, request

from . import bp
from .engine import DATASETS, load_graph, search


@bp.get("/")
def home():
    return render_template("index_shortest_path.html", datasets=DATASETS)


@bp.get("/api/solve")
def solve():
    try:
        size = int(request.args.get("graph", "13"))
        start = int(request.args.get("start", "0"))
        goal = int(request.args.get("goal", "1"))
        nodes, edges = load_graph(size)
        result = search(nodes, edges, start, goal, request.args.get("algorithm", "astar"))
    except ValueError:
        return jsonify(error="invalid_parameters"), 400
    return jsonify(nodes=[{"id": i, "x": x, "y": y} for i, (x, y) in nodes.items()],
                   edges=[{"source": a, "target": b, "weight": w} for a, b, w in edges],
                   **result)
