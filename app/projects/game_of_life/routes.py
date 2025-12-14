from . import bp
import os
import json
from flask import render_template, jsonify, request
from .game_of_life import GameOfLife
from .patterns import PATTERNS

game = GameOfLife(rows=30, cols=60)

# Folder to stock grids
BASE_DIR = os.path.dirname(__file__)
PATTERNS_DIR = os.path.join(BASE_DIR, 'static', 'patterns')
os.makedirs(PATTERNS_DIR, exist_ok=True)

def _pattern_path(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    if not safe:
        safe = "pattern"
    return os.path.join(PATTERNS_DIR, f"{safe}.json")

def apply_pattern(game, name: str, row: int, col: int):
    pattern = PATTERNS.get(name)
    if not pattern:
        return

    for dr, dc in pattern:
        r = row + dr
        c = col + dc
        if 0 <= r < game.rows and 0 <= c < game.cols:
            game.grid[r, c] = 1

# === Routes ===

@bp.route('/')
def home():
    # liste dynamique des patterns intégrés
    from .patterns import PATTERNS
    return render_template("index_game_of_life.html", patterns=sorted(PATTERNS.keys()))

@bp.route('/state')
def state():
    return jsonify(grid=game.to_list())

@bp.route('/next')
def next_step():
    game.step()
    return jsonify(grid=game.to_list())

@bp.route('/reset', methods=['POST'])
def reset():
    game.reset()
    return jsonify(success=True, grid=game.to_list())

@bp.route('/toggle', methods=['POST'])
def toggle():
    """Toggle the state of a cell. Expects 'row' and 'col' as form data."""
    data = request.get_json(silent=True) or {}
    r = int(data["row"])
    c = int(data["col"])
    # Basic validation
    if 0 <= r < game.rows and 0 <= c < game.cols:
        game.grid[r, c] = 1 - game.grid[r, c]  # Toggle between 0 and 1
        return jsonify(grid=game.to_list())
    
@bp.route('/clear', methods=['POST'])
def clear():
    game.grid.fill(0)
    return jsonify(success=True, grid=game.to_list())

@bp.post("/save")
def save_pattern():
    """Enregistre la grille actuelle sous un nom donné."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="Missing name"), 400

    path = _pattern_path(name)
    payload = {
        "name": name,
        "grid": game.to_list(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    return jsonify(ok=True)

@bp.post("/load")
def load_pattern():
    """Charge une grille enregistrée par son nom."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="Missing name"), 400

    path = _pattern_path(name)
    if not os.path.exists(path):
        return jsonify(ok=False, error="Pattern not found"), 404

    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    grid_list = payload.get("grid")
    if not grid_list:
        return jsonify(ok=False, error="Invalid pattern file"), 500

    game.from_list(grid_list)
    return jsonify(ok=True, grid=game.to_list())

@bp.get("/saved")
def list_saved():
    """Retourne la liste des patterns disponibles."""
    files = [
        f[:-5]  # retire .json
        for f in os.listdir(PATTERNS_DIR)
        if f.endswith(".json")
    ]
    return jsonify(patterns=sorted(files))

@bp.post("/pattern")
def generic_pattern():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    row = int(data.get("row",game.rows//2 ))
    col = int(data.get("col",game.cols//2 ))

    apply_pattern(game, name, row, col)

    return jsonify(grid=game.to_list())   