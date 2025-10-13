from flask import Blueprint

bp = Blueprint(
    "memory", __name__,
    template_folder="templates",
    static_folder="static"
)
from . import routes
