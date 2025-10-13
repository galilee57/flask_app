from . import bp
from flask import render_template

@bp.get("/")
def home():
    # ex: GET /memory
    return render_template("index_memory.html")
