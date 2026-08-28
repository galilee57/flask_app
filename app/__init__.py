from flask import Flask
from app.extensions import db, migrate
from app.config import get_config
from .blueprints import register_blueprints
from .factory import (
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
    )

    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)

    if app.config["ENV"] == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY doit être défini en production.")

    configure_logging(app)
    register_security_headers(app)
    configure_content(app)

    register_blueprints(app)
    load_project_catalogue(app)
    register_project_context(app)

    return app
