from . import bp
from flask import render_template, jsonify
import json


@bp.get("/")
def home():
    return render_template("index_projet_test.html")