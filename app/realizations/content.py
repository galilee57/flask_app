"""Editable bilingual sources for the realizations catalogue and case studies."""
from pathlib import Path
import json
import re
import unicodedata

import frontmatter
import yaml
from markdown import markdown


CONTENT_DIR = Path(__file__).resolve().parents[1] / "main/content/docs/realizations"
IMAGE_MANIFEST = Path(__file__).resolve().parent / "static/images/responsive/manifest.json"
THEMES = {
    "industry": {"fr": "Industrie & exploitation", "en": "Industry & operations"},
    "data": {"fr": "Données & IA", "en": "Data & AI"},
    "apps": {"fr": "Applications & automatisation", "en": "Apps & automation"},
    "making": {"fr": "Conception & fabrication", "en": "Design & fabrication"},
    "image": {"fr": "Image & acquisition", "en": "Imaging & capture"},
    "learning": {"fr": "Transmission & apprentissage", "en": "Sharing & learning"},
}
KINDS = {
    "education": {"fr": "Formation", "en": "Education"},
    "experience": {"fr": "Expérience", "en": "Experience"},
    "project": {"fr": "Projet", "en": "Project"},
    "hobby": {"fr": "Hobby", "en": "Hobby"},
}
VIEWS = ("selection", "all", "professional", "personal")


def load_projects(language):
    """Read on each request so Markdown edits need no application restart."""
    skill_registry = yaml.safe_load((CONTENT_DIR / "skills.yml").read_text(encoding="utf-8"))
    image_manifest = json.loads(IMAGE_MANIFEST.read_text()) if IMAGE_MANIFEST.exists() else {}
    projects = []
    for source_path in sorted(CONTENT_DIR.glob("*.fr.md")):
        if ".short." in source_path.name:
            continue
        canonical = frontmatter.load(source_path)
        slug = source_path.name.removesuffix(".fr.md")
        version = canonical.get("display_version", "long")
        if version not in {"long", "short"}:
            raise ValueError(f"{slug}: display_version must be long or short")
        suffix = f".short.{language}.md" if version == "short" else f".{language}.md"
        selected_path = CONTENT_DIR / (slug + suffix)
        source_language = language
        if not selected_path.exists():
            # Short mode can fall back to French short content, never to the long study.
            selected_path = CONTENT_DIR / (slug + (".short.fr.md" if version == "short" else ".fr.md"))
            source_language = "fr"
        if not selected_path.exists():
            raise ValueError(f"{slug}: missing {version} source")
        selected = canonical if selected_path == source_path else frontmatter.load(selected_path)
        project = dict(canonical.metadata, slug=slug, body=selected.content,
                       language=source_language, display_version=version)
        for field in ("title", "summary", "images", "related_ids"):
            if field in selected:
                project[field] = selected[field]
        if version == "short":
            project["images"] = selected.get("images", [])
            project["related_ids"] = selected.get("related_ids", [])
        project["kind"] = project.get("kind", "project")
        if project["kind"] not in KINDS:
            raise ValueError(f"{slug}: invalid kind")
        project["kind_label"] = KINDS[project["kind"]][language]
        project["summary"] = project.get("summary") or ""
        project["images"] = [dict(image, responsive=image_manifest.get(image["file"]))
                             for image in project.get("images", [])]
        project["skills"] = project.get("skills") or []
        project["year"] = project.get("year")
        project["skill_labels"] = [
            skill_registry.get(skill, {}).get(language, skill)
            for skill in project["skills"]
        ]
        projects.append(project)
    return sorted(projects, key=lambda project: (not project["featured"], project["id"]))


def _search_text(value):
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


def catalogue_context(language, args):
    projects = load_projects(language)
    view = args.get("view", "all")
    if view not in VIEWS:
        view = "all"
    theme = args.get("theme", "")
    if theme not in THEMES:
        theme = ""
    kind = args.get("kind", "")
    if kind not in KINDS:
        kind = ""
    query = args.get("q", "").strip()[:200]
    for project in projects:
        search = " ".join([project["id"], project["title"], project["summary"], project["kind_label"], *project["skill_labels"]])
        project["search"] = search
        project["visible"] = (
            (view == "all" or (view == "selection" and project["featured"])
             or view == project["origin"])
            and (not kind or kind == project["kind"])
            and (not theme or theme in project["themes"])
            and _search_text(query) in _search_text(search)
        )
    return dict(projects=projects, themes=THEMES, kinds=KINDS, view=view, theme=theme, kind=kind, query=query,
                result_count=sum(project["visible"] for project in projects))


def case_sections(project):
    """Keep source order and inline media; render one shared Jinja layout."""
    images = {image["id"]: image for image in project["images"]}
    body = re.sub(r"^# [^\n]+\n", "", project["body"], count=1)
    sections = []
    used = {key for key, image in images.items() if "ouverture" in image.get("emplacements", [])}
    opening_files = {images[key]["file"] for key in used}
    used_files = set(opening_files)
    # Drop editorial markers; section numbering supplies stable local anchors.
    body = re.sub(r"<!--\s*section:.*?-->", "", body, flags=re.S)
    body = re.sub(r"^#{1,6}[ \t]*$", "", body, flags=re.M)
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    introduction = re.sub(r"<!--.*?-->", "", parts[0], flags=re.S).strip()
    if introduction:
        sections.append({
            "id": "introduction",
            "title": "About the project" if project["language"] == "en" else "À propos du projet",
            "blocks": [{"html": markdown(introduction, extensions=["extra"])}],
        })
    for number in range(1, len(parts), 2):
        title, content = parts[number], parts[number + 1]
        blocks = []
        fragments = re.split(r"<!--\s*media:\s*([\w-]+).*?-->", content, flags=re.S)
        for index, fragment in enumerate(fragments):
            if index % 2:
                if fragment in images and fragment not in used and images[fragment]["file"] not in used_files:
                    blocks.append({"image": images[fragment]})
                    used.add(fragment)
                    used_files.add(images[fragment]["file"])
            else:
                fragment = re.sub(r"<!--[\s\S]*?-->", "", fragment).strip()
                if fragment:
                    blocks.append({"html": markdown(fragment, extensions=["extra"])})
        sections.append({"id": f"section-{len(sections) + 1}", "title": title, "blocks": blocks})
    remaining = []
    for key, image in images.items():
        if key not in used and image["file"] not in used_files:
            remaining.append({"image": image})
            used_files.add(image["file"])
    if remaining:
        gallery = next((section for section in sections
                        if re.search(r"galerie|gallery", section["title"], re.I)), None)
        if gallery is None:
            gallery = {"id": "gallery", "title": "Gallery" if project["language"] == "en" else "Galerie",
                       "blocks": []}
            sections.append(gallery)
        gallery["blocks"].extend(remaining)
    # A gallery needs an additional photo or raster illustration, rather than
    # just the generic SVG reference cards or a repeat of the opening image.
    raster_extensions = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
    return [section for section in sections
            if not re.search(r"galerie|gallery", section["title"], re.I)
            or any("image" in block
                   and block["image"]["file"] not in opening_files
                   and Path(block["image"]["file"]).suffix.lower() in raster_extensions
                   for block in section["blocks"])]
