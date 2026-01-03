from flask import Flask, request, session, g
from flask_flatpages import FlatPages
from .i18n_helpers import init_i18n
from app.extensions import db, migrate
from flask_migrate import Migrate
from app.config import get_config
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from .blueprints import register_blueprints   # 👈 import de la fonction de déclaration
import os, json
from flask import current_app
import yaml
import markdown
import traceback


migrate = Migrate()

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

    pages = FlatPages(app)

    # i18n : appel helpers langues et markdown i18n
    init_i18n(app, pages, languages=("en", "fr"), default_lang="fr")

    # 3) Blueprints commun & projets
    register_blueprints(app)

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

    # ------- Charger cartes.json depuis main/static/data -------
    main_bp = app.blueprints.get("main")
    if not main_bp:
        raise RuntimeError("Blueprint 'main' introuvable. Vérifie register_blueprints().")
    main_path = Path(main_bp.root_path)   # chemin vers app/main/
    cartes_path = main_path / "static" / "data" / "cartes.json"

    # ------- Injection automatique du footer -------
    @app.context_processor
    def inject_footer_resources():

        with cartes_path.open(encoding="utf-8") as f:
                cartes = json.load(f)
        
        # Stockage (clé = id du projet)
        app.config["PROJECT_CARDS"] = {c["id"]: c for c in cartes}

        bp_name = request.blueprint   # ex : "musculation", "game_of_life"
        card = app.config["PROJECT_CARDS"].get(bp_name)
        resources = card.get("resources", []) if card else []

        return {
            "resources": resources
        }

    @app.route("/_debug/flatpages-files")
    def debug_flatpages_files():
        fp = current_app.extensions["flatpages"]
        root = Path(current_app.config["FLATPAGES_ROOT"])
        ext = current_app.config["FLATPAGES_EXTENSION"].lstrip(".")  # "md"

        lines = []
        for f in sorted(root.rglob(f"*.{ext}")):
            rel = f.relative_to(root).as_posix()      # ex: docs/intro.fr.md
            page_id = rel[:-(len(ext)+1)]             # -> docs/intro.fr
            p = fp.get(page_id)
            lines.append(f"{'OK':2}  {page_id}" if p else f"NO  {page_id}   <-- {rel}")

        return "<pre>" + "\n".join(lines) + "</pre>"
    
    @app.route("/_debug/flatpages-parse")
    def debug_flatpages_parse():
        root = Path(current_app.config["FLATPAGES_ROOT"])
        ext = current_app.config["FLATPAGES_EXTENSION"].lstrip(".")  # md
        md_exts = current_app.config.get("FLATPAGES_MARKDOWN_EXTENSIONS", [])

        out = []
        for f in sorted(root.rglob(f"*.{ext}")):
            rel = f.relative_to(root).as_posix()
            try:
                txt = f.read_text(encoding="utf-8")
                # Parse front-matter très simple (--- ... ---)
                if not txt.startswith("---"):
                    raise ValueError("Front-matter: le fichier ne commence pas par '---'")
                _, fm, body = txt.split("---", 2)
                yaml.safe_load(fm)  # valide YAML
                markdown.markdown(body, extensions=md_exts)  # valide extensions Markdown
                out.append(f"OK   {rel}")
            except Exception as e:
                out.append(f"FAIL {rel}\n{type(e).__name__}: {e}\n{traceback.format_exc()}\n")

        return "<pre>" + "\n\n".join(out) + "</pre>"

    return app
