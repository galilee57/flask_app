from flask import Blueprint

bp = Blueprint(
    "a_star", __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes
