# app/blueprints.py
from flask import Flask

from .main import bp as main_bp
from .projects.todolist import bp as todolist_bp
from .projects.countries import bp as countries_bp
from .projects.memory import bp as memory_bp
from .projects.musculation import bp as musculation_bp
from .projects.phaser import bp as phaser_bp
from .projects.charts import bp as charts_bp
from .projects.game_of_life import bp as game_of_life_bp
from .projects.game_of_life_3d import bp as game_of_life_3d_bp
from .projects.viewer360 import bp as viewer_360_bp
from .experiences import bp as experiences_bp

def register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints de l'application via une boucle."""

    # Importer les modèles pour créer les tables
    from .projects.musculation import models as muscu_models
    from .projects.charts import models as charts_models

    blueprints = [
        (main_bp, "/"),
        (todolist_bp, "/projects/todolist"),
        (countries_bp, "/projects/countries"),
        (memory_bp, "/projects/memory"),
        (musculation_bp, "/projects/musculation"),
        (phaser_bp, "/projects/phaser"),
        (charts_bp, "/projects/charts"),
        (game_of_life_bp, "/projects/game_of_life"),
        (game_of_life_3d_bp, "/projects/game_of_life_3d"),
        (viewer_360_bp, "/projects/viewer360"),
        (experiences_bp, "/experiences")
    ]

    # Enregistrement via une boucle
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)
