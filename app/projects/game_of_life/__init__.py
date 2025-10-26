from flask import Blueprint

bp = Blueprint(
    "game_of_life", __name__,
    template_folder="templates",
    static_folder="static"
)
from . import routes
