from flask import Flask
from app.config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__, template_folder="main/templates", static_folder="main/static")
    
    # --- Configuration de l'application ---
    app.config.from_object(Config)

    # --- Blueprints commun & projets ---
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

    # --- Configuration des logs ---
    configure_logging(app)

    return app

def configure_logging(app):
    """Configure le logger Flask"""
    # Niveau minimal de logs (ex: DEBUG, INFO, WARNING, ERROR)
    app.logger.setLevel(logging.INFO)

    # Évite de dupliquer les logs en cas de reload
    if not app.logger.handlers:
        # Crée un dossier logs s'il n'existe pas
        os.makedirs("logs", exist_ok=True)

        # Fichier rotatif (évite les fichiers trop gros)
        file_handler = RotatingFileHandler("logs/app.log", maxBytes=100000, backupCount=3)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] in %(module)s: %(message)s"
        ))
        app.logger.addHandler(file_handler)

        app.logger.info("Logger configuré avec succès 🎯")