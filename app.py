from flask import Flask, render_template, abort, url_for
import json
import os

app = Flask(__name__)

# Chemin absolu vers le fichier cartes.json
cartes_path = os.path.join(os.path.dirname(__file__), "cartes.json")

# Charger les cartes
with open(cartes_path, encoding="utf-8") as f:
    cartes = json.load(f)

def list_static_files(subfolder):
    """
    Retourne l'ensemble (set) des chemins vers les fichiers
    situés dans app.static_folder/subfolder.
    Exemple : "css/mon_fichier.css".
    """
    full_path = os.path.join(app.static_folder, subfolder)
    if not os.path.isdir(full_path):
        return set()  # S'il n'y a pas de dossier "subfolder", on renvoie un ensemble vide.
    return {
        f"{subfolder}/{filename}"
        for filename in os.listdir(full_path)
        if os.path.isfile(os.path.join(full_path, filename))
    }

def list_template_files(subfolder):
    """
    Retourne l'ensemble (set) des chemins vers les fichiers
    situés dans app.template_folder/subfolder.
    Exemple : "projets/mon_projet.html".
    """
    full_path = os.path.join(app.template_folder, subfolder)
    if not os.path.isdir(full_path):
        return set()
    return {
        f"{subfolder}/{filename}"
        for filename in os.listdir(full_path)
        if os.path.isfile(os.path.join(full_path, filename))
    }

# Lister les fichiers statiques et templates disponibles
css_files = list_static_files("css")
js_files = list_static_files("js")
templates_disponibles = list_template_files("projets")

@app.route('/')
def index():
    """
    Page d'accueil listant toutes les cartes (ou projets).
    """
    return render_template("index.html", cartes=cartes)

@app.route('/projet/<projet_id>')
def page_projet(projet_id):
    """
    Page d’un projet précis, identifié par son ID.
    On vérifie si le projet existe, sinon on renvoie une erreur 404.
    """
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
