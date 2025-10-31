from flask import Flask
from app.extensions import db, migrate
from app.config import get_config
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="main/templates",
        static_folder="main/static",
        instance_relative_config=True,
    )

    # 1) Charger la config (inclut la DB)
    # - si config_name est fourni ("development" | "production"), on le respecte
    # - sinon get_config() résout via FLASK_CONFIG puis APP_ENV
    app.config.from_object(get_config(config_name))

    # 2) Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 3) Blueprints commun & projets
    from .main import bp as main
    app.register_blueprint(main, url_prefix="/")

    from .projects.todolist import bp as todolist_bp
    app.register_blueprint(todolist_bp, url_prefix="/projects/todolist")

    from .projects.countries import bp as countries_bp
    app.register_blueprint(countries_bp, url_prefix="/projects/countries")

    from .projects.memory import bp as memory_bp
    app.register_blueprint(memory_bp, url_prefix="/projects/memory")

    from .projects.musculation import bp as musculation_bp
    app.register_blueprint(musculation_bp, url_prefix="/projects/musculation")

    from .projects.phaser import bp as phaser_bp
    app.register_blueprint(phaser_bp, url_prefix="/projects/phaser")

    from .projects.charts import bp as charts_bp
    app.register_blueprint(charts_bp, url_prefix="/projects/charts")

    from .projects.game_of_life import bp as game_of_life_bp
    app.register_blueprint(game_of_life_bp, url_prefix="/projects/game_of_life")

    from .projects.game_of_life_3d import bp as game_of_life_3d_bp
    app.register_blueprint(game_of_life_3d_bp, url_prefix="/projects/game_of_life_3d")

    # 4) Logging simple (sans LOGS_DIR)
    app.logger.setLevel(logging.INFO)
    if not app.logger.handlers:
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            logs_dir / "app.log", maxBytes=100_000, backupCount=3
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] in %(module)s: %(message)s")
        )
        app.logger.addHandler(file_handler)

    app.logger.info(f"Application démarrée en mode {os.getenv('APP_ENV', 'prod')}")

    return app
