from flask import render_template

from . import bp
from .translations import MESSAGES


@bp.get("/")
def home():
    return render_template("index_tetris.html", tetris_translations=MESSAGES)
