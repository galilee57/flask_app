from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)

# Charger les projets depuis cartes.json
basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, "cartes.json"), encoding="utf-8") as f:
    cartes = json.load(f)

@app.route('/')
def index():
    return render_template("index.html", cartes=cartes)

@app.route('/projet/<projet_id>')
def page_projet(projet_id):
    projet = next((p for p in cartes if p["id"] == projet_id), None)
    if not projet:
        abort(404)

    # Exemple : templates/projets/projet_chart.html
    template_path = f"projets/{projet_id}.html"

    return render_template(template_path, projet=projet)

if __name__ == '__main__':
    app.run(debug=True)
