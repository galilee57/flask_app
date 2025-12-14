from flask import render_template
from . import bp

@bp.route("/")
def menu():
    # page qui liste Big Data, Machine Learning, etc.
    return render_template("experiences_menu.html")

@bp.route("/bigdata")
def bigdata():
    return render_template("bigdata/index_bigdata.html")

@bp.route("/machine_learning")
def machine_learning():
    return render_template("machine_learning/index_machine_learning.html")

@bp.route("/power_platform")
def power_platform():
    return render_template("power_platform/index_power_platform.html")

@bp.route("/web_design")
def web_design():
    return render_template("web_design/index_web_design.html")