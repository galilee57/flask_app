import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    DEBUG = False
    TESTING = False
    API_BASE_URL = ""  # utilisé côté templates

class DevConfig(Config):
    DEBUG = True
    API_BASE_URL = "http://127.0.0.1:5000/projects/todolist"  # serveur Flask en dev

class ProdConfig(Config):
    DEBUG = False
    API_BASE_URL = "/projects/todolist"  # même domaine que Flask en prod

def get_config():
    """Retourne la classe de config selon APP_ENV"""
    env = os.getenv("APP_ENV", "prod").lower()
    return DevConfig if env == "dev" else ProdConfig