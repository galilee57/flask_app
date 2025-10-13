from flask import Blueprint

bp = Blueprint(
    "charts", __name__,
    template_folder="templates",
    static_folder="static"
    #static_url_path="/charts/static"
)
from . import routes
