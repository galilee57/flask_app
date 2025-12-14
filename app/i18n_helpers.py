from __future__ import annotations
from flask import request, session, g

def init_i18n(app, pages, languages=("en", "fr"), default_lang="fr"):
    """Enregistre détection de langue + helpers Jinja dans l'app."""

    # --- Détection de langue (avant chaque requête) ---
    @app.before_request
    def _detect_lang():
        lang = request.args.get("lang")
        if lang in languages:
            session["lang"] = lang
        g.lang = session.get("lang", default_lang)

    # --- Résolution des pages FlatPages ---
    def _resolve_i18n_path(base_path: str, lang: str):
        p = pages.get(f"{base_path}.{lang}") or pages.get(base_path)
        return p

    # --- Helpers exposés aux templates ---
    def md_page_i18n(base_path: str, lang: str | None = None):
        lang = (lang or getattr(g, "lang", default_lang)) or default_lang
        return _resolve_i18n_path(base_path, lang)

    def md_html_i18n(base_path: str, lang: str | None = None) -> str:
        p = md_page_i18n(base_path, lang)
        return p.html if p else ""

    def md_meta_i18n(base_path: str, key: str, default=None, lang: str | None = None):
        p = md_page_i18n(base_path, lang)
        return p.meta.get(key, default) if p else default

    def current_lang():
        return getattr(g, "lang", default_lang)

    def t(translations: dict):
        lang = getattr(g, "lang", default_lang)
        return translations.get(lang, next(iter(translations.values()), ""))

    # --- Injection dans Jinja ---
    # Option A: via context_processor (un dict)
    @app.context_processor
    def _inject():
        return dict(
            t=t,
            md_page_i18n=md_page_i18n,
            md_html_i18n=md_html_i18n,
            md_meta_i18n=md_meta_i18n,
            current_lang=current_lang,
            LANGUAGES=languages,
        )

    # Option B (équivalente) : app.add_template_global(...)
    # app.add_template_global(t, "t")
    # app.add_template_global(md_page_i18n, "md_page_i18n")
    # app.add_template_global(md_html_i18n, "md_html_i18n")
    # app.add_template_global(md_meta_i18n, "md_meta_i18n")
    # app.add_template_global(current_lang, "current_lang")
