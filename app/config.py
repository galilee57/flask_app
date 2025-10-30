import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Répertoires robustes (pas de chemins relatifs)
BASE_DIR = Path(__file__).resolve().parent           # .../flask_app/app
PROJECT_DIR = BASE_DIR.parent                        # .../flask_app
INSTANCE_DIR = Path(os.environ.get("FLASK_INSTANCE_PATH", PROJECT_DIR / "instance"))
LOGS_DIR = PROJECT_DIR / "logs"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def _db_uri_from_env(default_path: Path) -> str:
    """DATABASE_URL si présent (Postgres, MySQL, etc.), sinon SQLite dans instance/."""
    url = os.getenv("DATABASE_URL")
    if url:    # ex: "sqlite:////home/USER/flask_app/instance/charts.db" ou postgres://...
        return url
    return f"sqlite:///{default_path}"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    DEBUG = False
    TESTING = False
    API_BASE_URL = ""                        # utilisé par tes templates
    SQLALCHEMY_DATABASE_URI = _db_uri_from_env(INSTANCE_DIR / "charts.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGS_DIR = LOGS_DIR

class DevConfig(Config):
    DEBUG = True
    ENV = "development"
    API_BASE_URL = "http://127.0.0.1:5000/projects/todolist"

class ProdConfig(Config):
    DEBUG = False
    ENV = "production"
    API_BASE_URL = "/projects/todolist"      # même domaine que Flask en prod

def get_config(name: str | None = None):
    """Retourne la classe de config selon le nom (development/production)."""
    if not name:
        name = os.getenv("FLASK_CONFIG", "development")
    mapping = {
        "development": DevConfig,
        "production": ProdConfig,
    }
    return mapping.get(name, ProdConfig)