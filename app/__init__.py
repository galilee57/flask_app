from flask import Flask
from app.extensions import db, migrate
from pathlib import Path
import os

from app.core.config import get_config, INSTANCE_DIR
from .core.blueprints import register_blueprints
from .core.factory import (
    configure_content,
    configure_logging,
    load_project_catalogue,
    register_project_context,
    register_security_headers,
)


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="main/templates",
        static_folder="main/static",
        instance_relative_config=True,
        instance_path=str(Path(os.getenv("FLASK_INSTANCE_PATH", INSTANCE_DIR)).resolve()),
    )

    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)

    if app.config["ENV"] == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY doit être défini en production.")

    if app.config["CONTAINER_MODE"]:
        if not os.getenv("DATABASE_URL") or not app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
            raise RuntimeError("Les conteneurs nécessitent DATABASE_URL PostgreSQL.")
        if not app.config.get("ADMIN_API_TOKEN"):
            raise RuntimeError("ADMIN_API_TOKEN doit être défini pour les conteneurs.")
        if app.config.get("TODOLIST_DATA_PATH") or app.config.get("PATTERN_STORAGE_DIR"):
            raise RuntimeError("Le stockage local partagé est interdit en mode conteneur.")

    from .core.deployment import configure_deployment
    configure_deployment(app)

    configure_logging(app)
    register_security_headers(app)
    configure_content(app)

    register_blueprints(app)
    load_project_catalogue(app)
    register_project_context(app)
    from .core.admin import configure_admin
    configure_admin(app)

    return app
