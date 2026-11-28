"""Public projects catalogue and case studies."""
from flask import Blueprint

bp = Blueprint("realizations", __name__, template_folder="templates", static_folder="static")

from . import routes
