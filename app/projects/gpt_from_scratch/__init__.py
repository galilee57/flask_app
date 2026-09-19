from flask import Blueprint

bp = Blueprint(
    "gpt_from_scratch", __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes
