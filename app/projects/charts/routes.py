from . import bp
from flask import render_template

@bp.route("/")
def index():
    # ex: GET /charts
    return render_template("index_charts.html", title="Charts")
