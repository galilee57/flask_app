# app/blueprints.py
from collections.abc import Iterable
from typing import NamedTuple

from flask import Blueprint, Flask

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
from .projects.projet_test import bp as projet_test_bp
from .projects.a_star import bp as a_star_bp
from .projects.sudoku import bp as sudoku_bp
from .experiences import bp as experiences_bp
from .projects.connect_four import bp as connect_four_bp
from .projects.snake import bp as snake_bp


class BlueprintRegistration(NamedTuple):
    blueprint: Blueprint
    url_prefix: str


BLUEPRINT_REGISTRY: tuple[BlueprintRegistration, ...] = (
    BlueprintRegistration(main_bp, "/"),
    BlueprintRegistration(todolist_bp, "/projects/todolist"),
    BlueprintRegistration(countries_bp, "/projects/countries"),
    BlueprintRegistration(memory_bp, "/projects/memory"),
    BlueprintRegistration(musculation_bp, "/projects/musculation"),
    BlueprintRegistration(phaser_bp, "/projects/phaser"),
    BlueprintRegistration(charts_bp, "/projects/charts"),
    BlueprintRegistration(game_of_life_bp, "/projects/game_of_life"),
    BlueprintRegistration(game_of_life_3d_bp, "/projects/game_of_life_3d"),
    BlueprintRegistration(viewer_360_bp, "/projects/viewer360"),
    BlueprintRegistration(projet_test_bp, "/projects/projet_test"),
    BlueprintRegistration(a_star_bp, "/projects/a_star"),
    BlueprintRegistration(sudoku_bp, "/projects/sudoku"),
    BlueprintRegistration(connect_four_bp, "/projects/connect_four"),
    BlueprintRegistration(snake_bp, "/projects/snake"),
    BlueprintRegistration(experiences_bp, "/experiences"),
)


def iter_blueprints() -> Iterable[BlueprintRegistration]:
    """Return every explicit application route registration in a stable order."""
    return BLUEPRINT_REGISTRY


def register_blueprints(app: Flask) -> None:
    """Register the explicit blueprint registry and import migration models."""

    # Importer les modèles pour créer les tables
    from .projects.charts import models as _charts_models
    from .projects.musculation import models as _muscu_models

    for registration in iter_blueprints():
        app.register_blueprint(
            registration.blueprint, url_prefix=registration.url_prefix
        )
