# app/projects/viewer360/__init__.py
from flask import Blueprint

bp = Blueprint(
    "viewer360",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",  # <- sera préfixé par /projects/viewer360 via register_blueprints
)

from . import routes  # noqa