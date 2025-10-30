import os
os.environ.setdefault("FLASK_CONFIG", "development")

from app import create_app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)