from flask import Blueprint

bp = Blueprint(
    "musculation", __name__,
    url_prefix="/projects/musculation",
    template_folder="templates",
    static_folder="static",
)
from . import routes
