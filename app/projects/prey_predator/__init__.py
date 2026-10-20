from flask import Blueprint

bp = Blueprint("prey_predator", __name__, template_folder="templates", static_folder="static")

from . import routes
