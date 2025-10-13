from . import bp
from flask import render_template

@bp.get("/")
def home():
    # ex: GET /phaser
    return render_template("index_phaser.html")
