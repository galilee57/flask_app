"""Public catalogue and case-study pages."""
from flask import abort, g, redirect, render_template, request, url_for

from . import bp
from .content import THEMES, case_sections, catalogue_context, load_projects


LEGACY_SLUGS = {
    "formation-arts-et-metiers": "f001",
    "formation-management-maintenance": "f002",
    "p017": "e001",
    "p021": "e002",
    "p025": "e003",
    "p030": "e004",
    "p020": "e007",
}


@bp.route("/")
def preview():
    return render_template("realizations/catalogue.html",
                           **catalogue_context(g.lang, request.args))


@bp.route("/projects/<slug>")
def case_study(slug):
    if slug in LEGACY_SLUGS:
        return redirect(url_for("realizations.case_study", slug=LEGACY_SLUGS[slug], lang=g.lang))
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
