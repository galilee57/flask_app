from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import Iterable, Tuple, Optional, Dict, Any
import re
import yaml
import markdown
from flask import current_app

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)

@dataclass(frozen=True)
class MDPage:
    slug: str
    lang: str
    meta: Dict[str, Any]
    html: str
    source_path: Path

def _parse_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    meta_raw, body = m.group(1), m.group(2)
    meta = yaml.safe_load(meta_raw) or {}
    return meta, body

def _mtime_key(path: Path) -> Tuple[str, int]:
    try:
        st = path.stat()
        return str(path), int(st.st_mtime)
    except FileNotFoundError:
        return str(path), 0

@lru_cache(maxsize=512)
def _render_cached(path_str: str, mtime: int, md_exts: Tuple[str, ...]) -> Tuple[Dict[str, Any], str]:
    p = Path(path_str)
    text = p.read_text(encoding="utf-8")
    meta, body = _parse_front_matter(text)
    html = markdown.markdown(body, extensions=list(md_exts))
    return meta, html

class MarkdownContent:
    """Mini-extension pour charger du contenu Markdown multilingue avec front matter."""
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("MDCONTENT_ROOT", Path(app.root_path).parent / "content")
        app.config.setdefault("MDCONTENT_DEFAULT_LANG", "fr")
        app.config.setdefault("MDCONTENT_FALLBACK_LANGS", ["en"])
        app.config.setdefault("MDCONTENT_MD_EXTENSIONS", ("extra", "fenced_code", "tables", "toc"))
        # Expose dans app.extensions et Jinja
        app.extensions["mdcontent"] = self
        app.jinja_env.globals["mdcontent"] = self.jinja_helper

    @property
    def root(self) -> Path:
        root = current_app.config["MDCONTENT_ROOT"]
        return Path(root)

    @property
    def md_extensions(self) -> Tuple[str, ...]:
        exts = current_app.config["MDCONTENT_MD_EXTENSIONS"]
        return tuple(exts)

    def _candidates(self, slug: str, lang: Optional[str]) -> Iterable[Tuple[str, Path]]:
        default_lang = current_app.config["MDCONTENT_DEFAULT_LANG"]
        langs: list[str] = []
        if lang:
            langs.append(lang)
        if default_lang not in langs:
            langs.append(default_lang)
        for fbl in current_app.config.get("MDCONTENT_FALLBACK_LANGS", []):
            if fbl not in langs:
                langs.append(fbl)
        for l in langs:
            yield l, self.root / l / f"{slug}.md"

    def get(self, slug: str, lang: Optional[str] = None, strict: bool = False) -> MDPage:
        """Retourne une page MDPage (meta + html). Si strict, n’essaie pas les fallbacks."""
        tried: list[Tuple[str, Path]] = []
        if strict and lang:
            tried = [(lang, self.root / lang / f"{slug}.md")]
        else:
            tried = list(self._candidates(slug, lang))

        for l, p in tried:
            if p.exists():
                key_path, key_mtime = _mtime_key(p)
                meta, html = _render_cached(key_path, key_mtime, self.md_extensions)
                return MDPage(slug=slug, lang=l, meta=meta, html=html, source_path=p)
        raise FileNotFoundError(f"Aucun contenu trouvé pour '{slug}' (lang={lang})")

    # Helper utilisable directement dans Jinja: {{ mdcontent('about').html|safe }}
    def jinja_helper(self, slug: str, lang: Optional[str] = None) -> MDPage:
        return self.get(slug, lang)
