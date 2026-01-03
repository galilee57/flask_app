from . import bp
from flask import render_template, jsonify, url_for, current_app
from . import bp
import json
import os

# Function to load project cards from a JSON file
def load_cartes():
    chemin = os.path.join(
        bp.root_path, "static", "data", "cartes.json"
    )
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)

# Home page
@bp.route("/")
def index():
    current_app.logger.info("Page d'accueil appelée")
    cartes = load_cartes()
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

# Endpoint to get all project cards
@bp.route("/data/cartes")
def cartes():
    cartes = load_cartes()

    # If in production filter published only
    is_prod = (
        os.getenv("FLASK_ENV") == "production"
        or current_app.config.get("ENV") == "production"
    )

    if is_prod:
        cartes = [c for c in cartes if c.get("published", True)]

    return jsonify(cartes)

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
    ignore_ext = {".pyc"}  # ajoute ce que tu veux filtrer

    paths = []
    for root, dirs, files in os.walk(base_dir):
        # filtrer certains dossiers et dossiers cachés
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for f in files:
            if f.startswith("."):
                continue
            if any(f.endswith(ext) for ext in ignore_ext):
                continue
            rel = os.path.relpath(os.path.join(root, f), base_dir)
            paths.append("/" + rel.replace(os.sep, "/"))

    paths.sort()
    return "<br>".join(paths)