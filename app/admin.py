"""Session authentication and catalogue-based private project previews."""
from hmac import compare_digest
from hashlib import sha256
import secrets
import time

from flask import abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash


def is_admin():
    from flask import current_app
    return (
        session.get("admin_until", 0) > time.time()
        and session.get("admin_username") == current_app.config.get("ADMIN_USERNAME")
        and session.get("admin_hash") == sha256((current_app.config.get("ADMIN_PASSWORD_HASH") or "").encode()).hexdigest()
        and bool(current_app.config.get("ADMIN_PASSWORD_HASH"))
    )


def can_view_drafts():
    return is_admin()


def configure_admin(app):
    def csrf_token():
        if "admin_csrf" not in session:
            session["admin_csrf"] = secrets.token_urlsafe(32)
        return session["admin_csrf"]

    def verify_csrf():
        expected = session.get("admin_csrf", "")
        if not expected or not compare_digest(expected, request.form.get("csrf_token", "")):
            abort(400)

    @app.context_processor
    def admin_context():
        return {"is_admin": is_admin(), "admin_csrf_token": csrf_token}

    @app.route("/admin", methods=["GET", "POST"])
    def admin_login():
        if is_admin():
            return redirect(url_for("main.lab"))
        error = None
        if request.method == "POST":
            verify_csrf()
            password_hash = app.config.get("ADMIN_PASSWORD_HASH")
            if not password_hash:
                abort(503, description="Accès admin non configuré.")
            password_valid = check_password_hash(password_hash, request.form.get("password", ""))
            username_valid = compare_digest(
                request.form.get("username", "").encode("utf-8"),
                app.config["ADMIN_USERNAME"].encode("utf-8"),
            )
            if username_valid and password_valid:
                lang = session.get("lang", "fr")
                session.clear()
                session.update(admin_username=app.config["ADMIN_USERNAME"], lang=lang, admin_until=time.time() + 3600, admin_hash=sha256(password_hash.encode()).hexdigest())
                return redirect(url_for("main.lab"))
            error = "Identifiant ou mot de passe incorrect."
        return render_template("admin.html", error=error)

    @app.post("/admin/logout")
    def admin_logout():
        verify_csrf()
        session.clear()
        return redirect(url_for("main.lab"))

    @app.before_request
    def protect_drafts():
        if can_view_drafts():
            return
        path = request.path.rstrip("/")
        cards = app.config["CARTES"]
        if path.startswith("/projects/"):
            project_id = path.split("/")[2]
            if not app.config["PROJECT_CARDS_BY_ID"].get(project_id, {}).get("published", False):
                abort(404)
        for card in cards:
            if card.get("published", False):
                continue
            project_path = "/projects/" + str(card["id"])
            image_path = "/static/images/" + card.get("image", "")
            blueprint_image_path = "/main/static/images/" + card.get("image", "")
            if path == project_path or path.startswith(project_path + "/"):
                abort(404)
            if card.get("image") and path in (image_path, blueprint_image_path):
                # Shared images remain available to published cards.
                if not any(c.get("published", False) and c.get("image") == card["image"] for c in cards):
                    abort(404)
        if path in ("/static/data/cartes.json", "/main/static/data/cartes.json"):
            abort(404)

    @app.after_request
    def private_cache(response):
        # Visibility depends on the session; shared caches must never store previews.
        if request.path.startswith("/admin") or can_view_drafts() or request.path in ("/data/cartes", "/lab", "/exploration"):
            response.headers["Cache-Control"] = "private, no-store"
            response.vary.add("Cookie")
        if is_admin() or request.path.startswith("/admin"):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response
