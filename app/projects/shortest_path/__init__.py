from flask import Blueprint

bp = Blueprint("shortest_path", __name__, template_folder="templates", static_folder="static")

from . import routes
