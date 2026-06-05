from flask import Blueprint

bp = Blueprint(
    "connect_four", __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes
