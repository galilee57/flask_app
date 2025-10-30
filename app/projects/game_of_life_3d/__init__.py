from flask import Blueprint

bp = Blueprint(
    "game_of_life_3d", __name__,
    template_folder="templates",
    static_folder="static"
)
from . import routes
