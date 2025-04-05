
from flask import Flask, render_template, url_for, abort
import json
import os

app = Flask(__name__)

basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, 'cartes.json'), encoding='utf-8') as f:
    cartes = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', cartes=cartes)

@app.route('/<projet_id>')
def page_projet(projet_id):
    projet = next((item for item in cartes if item['id'] == projet_id), None)
    if projet is None:
        abort(404)
    return render_template('projet.html', projet=projet)

if __name__ == '__main__':
    app.run()
