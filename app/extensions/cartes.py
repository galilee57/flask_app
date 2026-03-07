import json
from pathlib import Path

# Utilitaire pour charger les cartes depuis un fichier JSON
def load_cartes():
    path = Path("app/main/static/data/cartes.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_carte_by_id(carte_id):
    cartes = load_cartes()
    return next((c for c in cartes if c.get("id") == carte_id), None)