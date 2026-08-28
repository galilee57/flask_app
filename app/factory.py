"""Composable setup helpers used by :func:`app.create_app`."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from flask import Flask, request
from flask_flatpages import FlatPages

from .extensions.cartes import get_carte_by_id
from .i18n_helpers import init_i18n


def configure_logging(app: Flask) -> None:
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application configured for %s", app.config["ENV"])


def register_security_headers(app: Flask) -> None:
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        if app.config["ENV"] == "production":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


def configure_content(app: Flask) -> FlatPages:
    pages = FlatPages(app)
    init_i18n(app, pages, languages=("en", "fr"), default_lang="fr")
    return pages


def load_project_catalogue(app: Flask) -> None:
    """Load the project cards once, after the ``main`` blueprint is registered."""
    main_bp = app.blueprints.get("main")
    if main_bp is None:
        raise RuntimeError("Blueprint 'main' introuvable. Vérifie register_blueprints().")

    cartes_path = Path(main_bp.root_path) / "static" / "data" / "cartes.json"
    with cartes_path.open(encoding="utf-8") as catalogue_file:
        cartes: list[dict[str, Any]] = json.load(catalogue_file)

    app.config["CARTES"] = cartes
    app.config["PROJECT_CARDS_BY_ID"] = {
        str(card.get("id")): card for card in cartes
    }


def register_project_context(app: Flask) -> None:
    """Expose the existing footer resources and project card template globals."""
    @app.context_processor
    def inject_project_resources() -> dict[str, Any]:
        path = request.path
        if path.startswith("/projects/"):
            project_id = path.split("/")[2]
            card = app.config["PROJECT_CARDS_BY_ID"].get(project_id)

            # Retain the historical catalogue lookup as a fallback for callers
            # that populate the project map themselves.
            if card is None:
                card = get_carte_by_id(project_id)

            if card:
                return {"resources": card.get("resources", []), "project_card": card}

        return {"resources": []}
