"""Render model output as Markdown with no executable HTML."""

from urllib.parse import urlsplit

from markdown import Markdown
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup


class ModelLinks(Treeprocessor):
    def run(self, root):
        for element in root.iter():
            if element.tag == "img":
                element.tag = "span"
                element.text = element.attrib.pop("alt", "")
                element.attrib.clear()
            elif element.tag == "a":
                try:
                    url = urlsplit(element.get("href", ""))
                    allowed = url.scheme in {"https", "http"} and url.hostname
                except ValueError:
                    allowed = False
                if not allowed:
                    element.tag = "span"
                    element.attrib.clear()


def render_model_markdown(text):
    renderer = Markdown(extensions=["fenced_code", "sane_lists"])
    renderer.preprocessors.deregister("html_block")
    renderer.inlinePatterns.deregister("html")
    renderer.treeprocessors.register(ModelLinks(renderer), "safe_model_links", 5)
    return Markup(renderer.convert(text))
