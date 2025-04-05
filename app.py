from flask import Flask, render_template, abort, url_for
import json
import os

app = Flask(__name__)

# Chemin absolu vers le fichier cartes.json
cartes_path = os.path.join(os.path.dirname(__file__), "cartes.json")

# Charger les cartes
with open(cartes_path, encoding="utf-8") as f:
    cartes = json.load(f)

# Lister les fichiers statiques et templates dispo
def list_static_files(path):
    full_path = os.path.join("static", path)
    return {f"{path}/{f}" for f in os.listdir(full_path)} if os.path.exists(full_path) else set()

def list_template_files(path):
    full_path = os.path.join("templates", path)
    return {f"{path}/{f}" for f in os.listdir(full_path)} if os.path.exists(full_path) else set()

css_files = list_static_files("css")
js_files = list_static_files("js")
templates_disponibles = list_template_files("projets")

@app.route('/')
def index():
    return render_template("index.html", cartes=cartes)

@app.route('/<projet_id>')
def page_projet(projet_id):
    projet = next((p for p in cartes if p["id"] == projet_id), None)
    if not projet:
        abort(404)
    return render_template(
        "projet.html",
        projet=projet,
        css_files=css_files,
        js_files=js_files,
        templates=templates_disponibles
    )

if __name__ == '__main__':
    app.run(debug=True)

