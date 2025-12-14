from . import bp
from flask import render_template, jsonify, request
from .game_of_life_3d import GameOfLife3D

GAME = GameOfLife3D(shape=(48, 48, 48), rule_b=(5,), rule_s=(5, 6, 7,), density=0.05)

@bp.route('/')
def home():
    # ex: GET /countries
    return render_template("index_game_of_life_3d.html")

@bp.post("/config")
def update_config():
    data = request.get_json(silent=True) or {}

    rb = data.get("rule_b")   # ex "45" ou [4,5]
    rs = data.get("rule_s")   # ex "5678" ou [5,6,7,8]
    density = data.get("density")
    torus = data.get("torus")

    # Normalisation B/S
    def parse_rule(v):
        if v is None:
            return None
        if isinstance(v, str):
            return [int(ch) for ch in v if ch.isdigit()]
        return [int(x) for x in v]

    rule_b = parse_rule(rb)
    rule_s = parse_rule(rs)

    GAME.reconfigure(
        rule_b=rule_b,
        rule_s=rule_s,
        density=density,
        torus=torus,
        reset=True,        # on veut régénérer une grille
    )

    return jsonify(config=GAME.config(), alive=GAME.alive_coords())

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