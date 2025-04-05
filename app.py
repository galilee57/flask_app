
from flask import Flask, render_template, url_for, abort
import json
import os

app = Flask(__name__)

with open('cartes.json', encoding='utf-8') as f:
    cartes = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', cartes=cartes)

@app.route('/<project_id>')
def page_project(project_id):
    project = next((item for item in cartes if item['id'] == project_id), None)
    if project is None:
        abort(404)
    return render_template('project.html', project=project)

if __name__ == '__main__':
    app.run()
