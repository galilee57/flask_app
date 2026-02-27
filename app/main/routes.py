from __future__ import annotations

import json
import os
from pathlib import Path

from flask import current_app, jsonify, render_template, url_for
from . import bp


def load_cartes() -> list[dict]:
    """
    Charge les cartes.
    - Si create_app() a déjà chargé app.config["CARTES"], on l'utilise (recommandé).
    - Sinon fallback: lecture depuis main/static/data/cartes.json.
    """
    cached = current_app.config.get("CARTES")
    if cached is not None:
        return cached

    # Fallback (si tu n'as pas encore mis le preload dans create_app)
    chemin = Path(bp.root_path) / "static" / "data" / "cartes.json"
    with chemin.open(encoding="utf-8") as f:
        return json.load(f)


def filter_published_if_prod(cartes: list[dict]) -> list[dict]:
    is_prod = (
        os.getenv("FLASK_ENV") == "production"
        or current_app.config.get("ENV") == "production"
    )
    if is_prod:
        return [c for c in cartes if c.get("published", True)]
    return cartes


# Home page
@bp.route("/")
def index():
    current_app.logger.info("Page d'accueil appelée")
    return render_template("index.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/experiences_menu")
def experiences_menu():
    return render_template("experiences_menu.html")

@bp.route("/exploration")
def exploration():
    return render_template("exploration.html")

# Endpoint JSON: toutes les cartes
@bp.route("/data/cartes")
def cartes_json():
    cartes = filter_published_if_prod(load_cartes())
    return jsonify(cartes)


# Page LAB (rendu Jinja des cartes)
@bp.route("/lab")
def lab():
    cartes = filter_published_if_prod(load_cartes())

    # Mets ici le template qui contient:
    # {% for c in cartes %} {{ project_card(c, g.lang) }} {% endfor %}
    return render_template("exploration.html", cartes=cartes)

    # Si tu veux absolument réutiliser exploration.html, remplace par:
    # return render_template("exploration.html", cartes=cartes)


# Test CSS static file serving
@bp.route("/debug")
def debug():
    return f"""
    <p>Test du CSS :</p>
    <p><a href='{url_for("main.static", filename="css/style.css")}'>Ouvrir style.css</a></p>
    """


# Print all application routes in the browser
@bp.route("/map")
def map_urls():
    return "<br>".join(str(r) for r in current_app.url_map.iter_rules())


# Liste tous les fichiers sous app/, formaté comme /dossier/sousdossier/fichier.ext
@bp.route("/files-map")
def files_map():
    base_dir = current_app.root_path  # pointe sur .../app
    ignore_dirs = {"__pycache__", ".venv", ".git", ".mypy_cache", ".idea", ".pytest_cache"}
    ignore_ext = {".pyc"}

    paths: list[str] = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                continue
            if any(name.endswith(ext) for ext in ignore_ext):
                continue
            rel = os.path.relpath(os.path.join(root, name), base_dir)
            paths.append("/" + rel.replace(os.sep, "/"))

    paths.sort()
    return "<br>".join(paths)