from . import bp
import os
import json
from flask import render_template, jsonify, request, session
from .game_of_life import GameOfLife
from .patterns import PATTERNS

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

def _get_game() -> GameOfLife:
    rows = int(session.get("rows", 30))
    cols = int(session.get("cols", 60))
    grid = session.get("grid")

    game = GameOfLife(rows=rows, cols=cols, random_init=False)
    if grid:
        game.from_list(grid)
    return game

def _save_game(game: GameOfLife) -> None:
    session["rows"] = game.rows
    session["cols"] = game.cols
    session["grid"] = game.to_list()
    session.modified = True

# === Routes ===

@bp.route('/')
def home():
    return render_template("index_game_of_life.html", patterns=sorted(PATTERNS.keys()))

@bp.post("/grid")
def set_grid():
    """Recrée une grille vide avec une nouvelle taille. POST {rows, cols}"""
    data = request.get_json(silent=True) or {}
    rows = int(data.get("rows", 60))
    cols = int(data.get("cols", 60))

    rows = max(5, min(rows, 300))
    cols = max(5, min(cols, 300))

    # ✅ vide
    game = GameOfLife(rows=rows, cols=cols, random_init=False)
    _save_game(game)
    return jsonify(grid=game.to_list(), rows=game.rows, cols=game.cols)

@bp.route('/state')
def state():
    game = _get_game()
    return jsonify(grid=game.to_list(), rows=game.rows, cols=game.cols)

@bp.route('/next')
def next_step():
    game = _get_game()
    game.step()
    _save_game(game)
    return jsonify(grid=game.to_list(), rows=game.rows, cols=game.cols)

@bp.route('/reset', methods=['POST'])
def reset():
    game = _get_game()
    game.reset()
    _save_game(game)
    return jsonify(success=True, grid=game.to_list())

@bp.route('/toggle', methods=['POST'])
def toggle():
    game = _get_game()
    data = request.get_json(silent=True) or {}
    if "row" not in data or "col" not in data:
        return jsonify(ok=False, error="Missing row/col"), 400

    r = int(data["row"])
    c = int(data["col"])

    if not (0 <= r < game.rows and 0 <= c < game.cols):
        return jsonify(ok=False, error="Out of bounds"), 400

    game.grid[r, c] = 1 - game.grid[r, c]
    _save_game(game)
    return jsonify(ok=True, grid=game.to_list(), rows=game.rows, cols=game.cols)

@bp.route('/clear', methods=['POST'])
def clear():
    game = _get_game()
    game.clear()
    _save_game(game)
    return jsonify(success=True, grid=game.to_list())

@bp.post("/save")
def save_pattern():
    game = _get_game()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="Missing name"), 400

    path = _pattern_path(name)
    payload = {"name": name, "grid": game.to_list()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    return jsonify(ok=True)

@bp.post("/load")
def load_pattern():
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

    game = _get_game()
    game.from_list(grid_list)
    _save_game(game)
    return jsonify(ok=True, grid=game.to_list())

@bp.get("/saved")
def list_saved():
    files = [f[:-5] for f in os.listdir(PATTERNS_DIR) if f.endswith(".json")]
    return jsonify(patterns=sorted(files))

@bp.post("/pattern")
def generic_pattern():
    game = _get_game()
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    row = int(data.get("row", game.rows // 2))
    col = int(data.get("col", game.cols // 2))

    apply_pattern(game, name, row, col)
    _save_game(game)
    return jsonify(grid=game.to_list(), rows=game.rows, cols=game.cols)