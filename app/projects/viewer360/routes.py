# app/projects/viewer360/routes.py
from pathlib import Path
from flask import render_template, jsonify, url_for
from . import bp

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


@bp.get("/")
def home():
    return render_template("index_viewer360.html")


@bp.get("/api/images")
def api_images():
    static_root = Path(bp.static_folder)       # .../viewer360/static
    images_root = static_root / "images"       # .../viewer360/static/images

    items = []
    if images_root.exists():
        for p in sorted(images_root.iterdir()):
            if p.is_file() and p.suffix.lower() in ALLOWED_EXT:
                items.append({
                    "name": p.name,
                    "url": url_for("viewer360.static",
                                   filename=f"images/{p.name}")
                })

    return jsonify({"items": items})
