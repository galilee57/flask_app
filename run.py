import os
from app import create_app

if __name__ == "__main__":
    os.environ.setdefault("FLASK_CONFIG", "development")
    app = create_app()
    app.run(debug=True)