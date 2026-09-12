"""Smoke tests for public pages and their directly referenced local assets."""

from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest


PUBLIC_PAGES = (
    "/", "/about", "/experiences_menu", "/exploration", "/lab",
    "/experiences/", "/experiences/big_data", "/experiences/machine_learning",
    "/experiences/power_platform", "/experiences/web_design",
    "/experiences/deep_learning", "/experiences/fablab",
    "/projects/todolist/", "/projects/countries/", "/projects/memory/",
    "/projects/musculation/", "/projects/phaser/", "/projects/charts/",
    "/projects/game_of_life/", "/projects/game_of_life_3d/",
    "/projects/viewer360/", "/projects/projet_test/", "/projects/a_star/",
    "/projects/tetris/", "/projects/sudoku/", "/projects/connect_four/", "/projects/snake/",
)


class PageAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
        self.has_main = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.has_main |= tag == "main"
        resource = attrs.get("src")
        if tag == "link" and attrs.get("rel") in ("stylesheet", "icon"):
            resource = attrs.get("href")
        if resource:
            url = urlsplit(resource)
            if not url.scheme and not url.netloc and url.path.startswith("/"):
                self.urls.add(resource)


@pytest.mark.parametrize("path", PUBLIC_PAGES)
@pytest.mark.parametrize("language", ("fr", "en"))
def test_public_page_and_local_assets_are_available(client, path, language):
    response = client.get(path, query_string={"lang": language})
    assert response.status_code == 200, path
    assert response.mimetype == "text/html"
    html = response.get_data(as_text=True)
    assert "[i18n]" not in html
    page = PageAssets()
    page.feed(html)
    assert page.has_main, f"Missing main content: {path}"
    assert page.urls, f"No local assets found: {path}"
    for asset in sorted(page.urls):
        resource = client.get(asset)
        assert resource.status_code == 200, f"{path}: {asset}"


def test_compiled_tailwind_stylesheet_is_served(client):
    response = client.get("/static/css/output.css")
    assert response.status_code == 200
    assert response.mimetype == "text/css"
    css = response.get_data(as_text=True)
    assert "tailwindcss" in css
    assert "--color-primary-500" in css
    assert ".flex" in css


def test_home_language_defaults_to_french_and_remembers_selection(client):
    assert "Bienvenue sur mon site !" in client.get("/").get_data(as_text=True)
    assert "Welcome to my site !" in client.get("/?lang=en").get_data(as_text=True)
    assert "Welcome to my site !" in client.get("/").get_data(as_text=True)
    assert "Welcome to my site !" in client.get("/?lang=unsupported").get_data(as_text=True)
    assert "Bienvenue sur mon site !" in client.get("/?lang=fr").get_data(as_text=True)


def test_language_selection_is_isolated_between_visitors(app):
    english_visitor = app.test_client()
    english_visitor.get("/?lang=en")
    new_visitor = app.test_client()
    assert "Bienvenue sur mon site !" in new_visitor.get("/").get_data(as_text=True)


def test_unknown_page_returns_404(client):
    assert client.get("/page-that-does-not-exist").status_code == 404


def test_markdown_code_highlighting_dependency_is_functional():
    from markdown import markdown

    html = markdown("```python\nprint('hello')\n```", extensions=["fenced_code", "codehilite"])
    assert 'class="codehilite"' in html
    assert "<span" in html, "Pygments must highlight code, not just wrap it"
