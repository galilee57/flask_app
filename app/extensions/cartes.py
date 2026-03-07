import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CARTES_PATH = BASE_DIR / "main" / "static" / "data" / "cartes.json"

def load_cartes():
    with open(CARTES_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_carte_by_id(carte_id):
    cartes = load_cartes()
    return next((c for c in cartes if c.get("id") == carte_id), None)