from flask import Flask, request
from flask_flatpages import FlatPages
from .i18n_helpers import init_i18n
from app.extensions import db, migrate
from app.config import get_config
from .blueprints import register_blueprints
from pathlib import Path
import os, json, logging

def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="main/templates",
        static_folder="main/static",
        instance_relative_config=True,
    )

    # 1) Config: pilotée par FLASK_CONFIG (prod/dev) + DATABASE_URL
    app.config.from_object(get_config(config_name))

    # 2) Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Logs utiles (dans error.log PythonAnywhere)
    app.logger.setLevel(logging.INFO)
    app.logger.info("ENV=%s FLASK_CONFIG=%s", app.config.get("ENV"), os.environ.get("FLASK_CONFIG"))
    app.logger.info("DB=%s", app.config.get("SQLALCHEMY_DATABASE_URI"))

    pages = FlatPages(app)
    init_i18n(app, pages, languages=("en", "fr"), default_lang="fr")

    register_blueprints(app)

    # ------- Charger cartes.json depuis main/static/data -------
    main_bp = app.blueprints.get("main")
    if not main_bp:
        raise RuntimeError("Blueprint 'main' introuvable. Vérifie register_blueprints().")
    main_path = Path(main_bp.root_path)
    cartes_path = main_path / "static" / "data" / "cartes.json"

    @app.context_processor
    def inject_footer_resources():
        with cartes_path.open(encoding="utf-8") as f:
            cartes = json.load(f)

        app.config["PROJECT_CARDS"] = {c["id"]: c for c in cartes}

        bp_name = request.blueprint
        card = app.config["PROJECT_CARDS"].get(bp_name)
        resources = card.get("resources", []) if card else []

        return {"resources": resources}

    return app