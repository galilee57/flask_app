from flask import render_template
from . import bp

@bp.route("/")
def menu():
    # page qui liste Big Data, Machine Learning, etc.
    return render_template("experiences_menu.html")

@bp.route("/big_data")
def big_data():
    return render_template("big_data/index_big_data.html")

@bp.route("/machine_learning")
def machine_learning():
    return render_template("machine_learning/index_machine_learning.html")

@bp.route("/power_platform")
def power_platform():
    return render_template("power_platform/index_power_platform.html")

@bp.route("/web_design")
def web_design():
    return render_template("web_design/index_web_design.html")

@bp.route("/deep_learning")
def deep_learning():
    return render_template("deep_learning/index_deep_learning.html")

@bp.route("/fablab")
def fablab():
    return render_template("fablab/index_fablab.html")