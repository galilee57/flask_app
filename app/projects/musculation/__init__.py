from flask import Blueprint

bp = Blueprint(
    "musculation", __name__,
    template_folder="templates",
    static_folder="static"
)
from . import routes
