from __future__ import annotations

from . import bp
from flask import render_template, jsonify, request, session
from .game_of_life_3d import GameOfLife3D

from uuid import uuid4
from threading import Lock
from dataclasses import dataclass, field
import time


# --- Store en mémoire : 1 univers = 1 GameOfLife3D + lock + version
@dataclass
class Universe:
    game: GameOfLife3D
    version: int = 0
    lock: Lock = field(default_factory=Lock)
    updated_at: float = field(default_factory=time.time)

UNIVERSES: dict[str, Universe] = {}


def _new_universe(*, shape=(48, 48, 48), rule_b=(5,), rule_s=(5, 6, 7), density=0.05, torus=True, seed=None) -> tuple[str, Universe]:
    uid = uuid4().hex
    u = Universe(
        game=GameOfLife3D(shape=shape, rule_b=rule_b, rule_s=rule_s, density=density, torus=torus, seed=seed),
        version=0,
    )
    UNIVERSES[uid] = u
    return uid, u


def _get_or_create_universe() -> tuple[str, Universe]:
    uid = session.get("gol_uid")
    u = UNIVERSES.get(uid) if uid else None
    if u is None:
        uid, u = _new_universe()
        session["gol_uid"] = uid
        session["gol_version"] = u.version
    return uid, u


def _json_state(uid: str, u: Universe):
    g = u.game
    return jsonify(
        universe_id=uid,
        version=u.version,
        config=g.config(),
        alive=g.alive_coords(),
    )


# ---- routes

@bp.route("/")
def home():
    return render_template("index_game_of_life_3d.html")


@bp.get("/state")
def state():
    uid, u = _get_or_create_universe()
    return _json_state(uid, u)


@bp.post("/next")
def next_step():
    uid, u = _get_or_create_universe()

    payload = request.get_json(silent=True) or {}
    client_uid = payload.get("universe_id")
    client_ver = payload.get("version")

    # Refuse si tick d'un ancien run (réponse côté client: ignorer)
    if client_uid != uid or client_ver != u.version:
        return jsonify(error="stale"), 409

    with u.lock:
        # re-check (au cas où)
        if session.get("gol_uid") != uid or session.get("gol_version") != u.version:
            return jsonify(error="stale"), 409

        u.game.step()
        u.updated_at = time.time()

    return _json_state(uid, u)


@bp.post("/reset")
def reset():
    data = request.get_json(silent=True) or {}
    density = data.get("density", 0.05)
    seed = data.get("seed", None)

    # Nouveau run : nouvel univers_id (le plus robuste)
    uid, u = _new_universe(density=float(density), seed=seed)

    session["gol_uid"] = uid
    session["gol_version"] = u.version

    return _json_state(uid, u)


@bp.post("/config")
def update_config():
    data = request.get_json(silent=True) or {}

    rb = data.get("rule_b")
    rs = data.get("rule_s")
    density = data.get("density", 0.05)
    torus = data.get("torus", True)
    seed = data.get("seed", None)

    # Normalisation B/S
    def parse_rule(v):
        if v is None:
            return None
        if isinstance(v, str):
            return [int(ch) for ch in v if ch.isdigit()]
        return [int(x) for x in v]

    rule_b = parse_rule(rb) or (5,)
    rule_s = parse_rule(rs) or (5, 6, 7)

    # Nouveau run à chaque config (évite intercalage)
    uid, u = _new_universe(rule_b=tuple(rule_b), rule_s=tuple(rule_s),
                          density=float(density), torus=bool(torus), seed=seed)

    session["gol_uid"] = uid
    session["gol_version"] = u.version

    return _json_state(uid, u)