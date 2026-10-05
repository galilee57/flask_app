from flask import Blueprint

bp = Blueprint("snow_layers", __name__, template_folder="templates", static_folder="static")

from . import routes
