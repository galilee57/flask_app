from . import bp
from flask import render_template, jsonify
from .game_of_life import GameOfLife

game = GameOfLife(rows=30, cols=60)

@bp.route('/')
def home():
    # ex: GET /countries
    return render_template("index_game_of_life.html")

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
    return jsonify(success=True)