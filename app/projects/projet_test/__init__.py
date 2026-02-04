from flask import Blueprint

bp = Blueprint(
    "projet_test", __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes
