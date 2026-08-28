from flask import Flask, request, g
from flask_flatpages import FlatPages
from .i18n_helpers import init_i18n
from app.extensions import db, migrate
from app.config import get_config
from .blueprints import register_blueprints
from pathlib import Path
import os, json, logging
from .extensions.cartes import get_carte_by_id


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="main/templates",
        static_folder="main/static",
        instance_relative_config=True,
    )

    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)

    if app.config["ENV"] == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY doit être défini en production.")

    app.logger.setLevel(logging.INFO)
    app.logger.info("Application configured for %s", app.config["ENV"])

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if app.config["ENV"] == "production":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    pages = FlatPages(app)
    init_i18n(app, pages, languages=("en", "fr"), default_lang="fr")

    register_blueprints(app)

    # ------- Charger cartes.json depuis main/static/data (1 seule fois) -------
    main_bp = app.blueprints.get("main")
    if not main_bp:
        raise RuntimeError("Blueprint 'main' introuvable. Vérifie register_blueprints().")

    main_path = Path(main_bp.root_path)
    cartes_path = main_path / "static" / "data" / "cartes.json"

    with cartes_path.open(encoding="utf-8") as f:
        cartes = json.load(f)

    app.config["CARTES"] = cartes
    app.config["PROJECT_CARDS_BY_ID"] = {str(c.get("id")): c for c in cartes}

    # ------- Footer resources: basé sur g.project_id (Option A) -------
    @app.context_processor
    def inject_project_resources():
        path = request.path

        if path.startswith("/projects/"):
            project_id = path.split("/")[2]

            card = get_carte_by_id(project_id)

            if card:
                return {
                    "resources": card.get("resources", []),
                    "project_card": card
                }

        return {"resources": []}

    return app
