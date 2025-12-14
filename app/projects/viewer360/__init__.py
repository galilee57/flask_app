from flask import Blueprint

bp = Blueprint(
    "viewer360",
    __name__,
    template_folder="templates",
    static_folder="static",                 # -> app/projects/viewer360/static
    static_url_path="/viewer360/static"     # URL publique pour le static
)

from . import routes
