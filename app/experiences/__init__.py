from flask import Blueprint

bp = Blueprint(
    "experiences",        # 👈 nom du blueprint
    __name__,
    template_folder="templates",
)

# On importe les routes pour enregistrer les vues sur ce blueprint
from . import routes          # menu / page principale