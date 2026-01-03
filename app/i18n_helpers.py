from __future__ import annotations
from flask import request, session, g, current_app
import re

def init_i18n(app, pages, languages=("en", "fr"), default_lang="fr"):
    @app.before_request
    def _detect_lang():
        lang = request.args.get("lang")
        if lang in languages:
            session["lang"] = lang
        g.lang = session.get("lang", default_lang)

    def _resolve_i18n_path(base_path: str, lang: str):
        return pages.get(f"{base_path}.{lang}") or pages.get(base_path)

    def _missing(msg: str, fallback=""):
        # En dev on affiche une alerte claire dans la page HTML
        if app.debug:
            return f"[i18n] {msg}"
        return fallback

    def md_page_i18n(base_path: str, lang: str | None = None):
        lang = (lang or getattr(g, "lang", default_lang)) or default_lang
        p = _resolve_i18n_path(base_path, lang)
        return p

    def md_html_i18n(base_path: str, lang: str | None = None) -> str:
        p = md_page_i18n(base_path, lang)
        if not p:
            return _missing(f"Page introuvable: '{base_path}' (lang={getattr(g,'lang',default_lang)})", "")
        return p.html

    def md_meta_i18n(base_path: str, key: str, default=None, lang: str | None = None):
        p = md_page_i18n(base_path, lang)
        if not p:
            return _missing(f"Meta: page introuvable: '{base_path}' (key={key})", default)
        return p.meta.get(key, default)

    def current_lang():
        return getattr(g, "lang", default_lang)

    def t(translations: dict):
        lang = getattr(g, "lang", default_lang)
        return translations.get(lang, next(iter(translations.values()), ""))

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
