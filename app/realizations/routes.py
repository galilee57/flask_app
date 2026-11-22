"""Admin-only catalogue and case-study pages, separate from legacy experiences."""
from flask import abort, g, render_template, request

from app.core.admin import can_view_drafts
from . import bp
from .content import THEMES, case_sections, catalogue_context, load_projects


@bp.before_request
def protect_preview():
    # Includes the blueprint's media and scripts, not just its HTML pages.
    if not can_view_drafts():
        abort(404)


@bp.route("/")
def preview():
    return render_template("realizations/catalogue.html",
                           **catalogue_context(g.lang, request.args))


@bp.route("/projects/<slug>")
def case_study(slug):
    projects = load_projects(g.lang)
    project = next((item for item in projects
                    if item["slug"] == slug and item.get("detail")), None)
    if project is None:
        abort(404)
    return render_template("realizations/case_study.html", project=project,
                           sections=case_sections(project), themes=THEMES,
                           related=[item for item in projects
                                    if item.get("detail") and item["slug"] != slug
                                    and item["id"] in project.get("related_ids", [])][:3])
