from . import bp
from flask import render_template, jsonify, request
from .game_of_life_3d import GameOfLife3D

GAME = GameOfLife3D(shape=(48, 48, 48), rule_b=(5,), rule_s=(5, 6, 7,), density=0.05)

@bp.route('/')
def home():
    # ex: GET /countries
    return render_template("index_game_of_life_3d.html")

@bp.route('/state')
def state():
    return jsonify(config=GAME.config(), alive=GAME.alive_coords())

@bp.route('/next')
def next_step():
    GAME.step()
    return jsonify(config=GAME.config(), alive=GAME.alive_coords())

@bp.route('/reset', methods=['POST'])
def reset():
    data = request.get_json(silent=True) or {}
    density = data.get('density')
    seed = data.get('seed')
    GAME.reset(density=density, seed=seed)
    return jsonify(config=GAME.config(), alive=GAME.alive_coords())