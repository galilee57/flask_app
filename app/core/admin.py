"""Session authentication and catalogue-based private project previews."""
from hmac import compare_digest
from hashlib import sha256
import secrets
import time

from flask import abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .llm import ERROR_MESSAGES, MAX_PROMPT_LENGTH, LLMError
from .rag import (
    RAG_ERRORS, RagError, answer_from_projects, answer_from_summary, compare_offer, load_portfolio_summary,
)
from .rag_rebuild import rebuild_state, start_rag_rebuild
from .response_markdown import render_model_markdown


def is_admin():
    from flask import current_app
    try:
        opened_session = session._get_current_object()
    except (AssertionError, RuntimeError):
        # Error responses can run before Flask has opened a session.
        return False
    return (
        opened_session.get("admin_until", 0) > time.time()
        and opened_session.get("admin_username") == current_app.config.get("ADMIN_USERNAME")
        and opened_session.get("admin_hash") == sha256((current_app.config.get("ADMIN_PASSWORD_HASH") or "").encode()).hexdigest()
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

    @app.route("/admin/llm", methods=["GET", "POST"])
    def admin_llm():
        if not is_admin():
            if request.method == "POST":
                abort(403)
            return redirect(url_for("admin_login"))

        provider = app.config["LLM_PROVIDER"]
        model = {"local": app.config["LLM_LOCAL_MODEL"], "openai": app.config["OPENAI_MODEL"]}.get(provider)
        prompt = ""
        answer = error = summary = None
        sources = []
        mode = "passages"
        truncated = False
        status = 200
        if request.method == "GET" and request.args.get("summary") == "skills":
            try:
                summary = load_portfolio_summary(g.lang)
            except RagError as exc:
                error = RAG_ERRORS[str(exc)]
                status = 503
        if request.method == "POST":
            verify_csrf()
            prompt = request.form.get("prompt", "").strip()
            mode = request.form.get("mode", "passages")
            if request.form.get("use_rag") == "on":
                mode = "passages"
            if mode not in {"passages", "summary", "offer"}:
                abort(400)
            if not 1 <= len(prompt) <= MAX_PROMPT_LENGTH:
                error = {
                    "fr": f"Saisis entre 1 et {MAX_PROMPT_LENGTH} caractères.",
                    "en": f"Enter 1 to {MAX_PROMPT_LENGTH} characters.",
                }
                prompt = prompt[:MAX_PROMPT_LENGTH]
                status = 400
            else:
                try:
                    if mode == "summary":
                        summary = load_portfolio_summary(g.lang)
                        answer, truncated = answer_from_summary(prompt, g.lang, summary)
                    elif mode == "offer":
                        answer, sources, truncated = compare_offer(prompt, g.lang)
                    else:
                        answer, sources, truncated = answer_from_projects(prompt, g.lang)
                except RagError as exc:
                    error = RAG_ERRORS[str(exc)]
                    status = 503
                except LLMError as exc:
                    error = ERROR_MESSAGES[str(exc)]
                    status = 503 if str(exc) == "configuration" else 502

        return render_template(
            "admin_llm.html", provider=provider, model=model, prompt=prompt,
            answer=render_model_markdown(answer) if answer else None, error=error,
            max_length=MAX_PROMPT_LENGTH, sources=sources, mode=mode, truncated=truncated,
            summary=summary, embedding_provider=app.config["RAG_EMBEDDING_PROVIDER"],
            rebuild_status=rebuild_state() if app.config["ENV"] == "development" else None,
        ), status

    @app.post("/admin/llm/rebuild")
    def admin_rag_rebuild():
        if app.config["ENV"] != "development":
            abort(404)
        if not is_admin():
            abort(403)
        verify_csrf()
        start_rag_rebuild()
        return redirect(url_for("admin_llm"), code=303)

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
