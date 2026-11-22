"""Private preview of the future projects section."""
from flask import Blueprint

bp = Blueprint("realizations", __name__, template_folder="templates", static_folder="static")

from . import routes
