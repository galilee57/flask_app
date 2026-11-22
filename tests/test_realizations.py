"""Contracts for the editable catalogue, reviewed studies and legacy entry points."""
from html.parser import HTMLParser
import re

import frontmatter
import pytest

from app.realizations import content


@pytest.fixture
def admin_client(client, app):
    from werkzeug.security import generate_password_hash

    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('test-password')
    client.get('/admin')
    with client.session_transaction() as session:
        csrf = session['admin_csrf']
    response = client.post('/admin', data={
        'csrf_token': csrf, 'username': app.config['ADMIN_USERNAME'],
        'password': 'test-password',
    })
    assert response.status_code == 302
    return client


class Projects(HTMLParser):
    def __init__(self):
        super().__init__()
        self.visible = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-project' in attrs and 'hidden' not in attrs:
            self.visible.append(attrs)


@pytest.mark.parametrize('entry', ['/realizations/'])
@pytest.mark.parametrize('language', ['fr', 'en'])
def test_catalogue_preview_includes_reviewed_studies(admin_client, entry, language):
    response = admin_client.get(entry, query_string={'lang': language, 'view': 'selection'})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    parser = Projects()
    parser.feed(html)
    assert len(parser.visible) == 3
    assert all(card['data-featured'] == 'true' for card in parser.visible)
    assert '/realizations/projects/pp001' in html
    assert '/realizations/projects/pp002' in html
    assert '/realizations/projects/pp019' in html
    assert '[i18n]' not in html
    assert '"Pro", "en": "Skills"' not in html


@pytest.mark.parametrize('query,expected', [
    ({'view': 'personal'}, 20),
    ({'view': 'professional'}, 64),
    ({'view': 'all'}, 84),
    ({'view': 'all', 'q': 'PP001'}, 1),
    ({'view': 'all', 'q': 'refractaires'}, 1),
    ({'view': 'professional', 'theme': 'image'}, 2),
    ({'view': 'all', 'q': '<script>missing</script>'}, 0),
])
def test_filters_work_without_javascript(admin_client, query, expected):
    response = admin_client.get('/realizations/', query_string=query)
    html = response.get_data(as_text=True)
    parser = Projects()
    parser.feed(html)
    assert len(parser.visible) == expected
    assert '<script>missing</script>' not in html


@pytest.mark.parametrize('slug', ['pp001', 'pp002'])
@pytest.mark.parametrize('language', ['fr', 'en'])
def test_case_study_preserves_markdown_sections_and_serves_media(admin_client, slug, language):
    response = admin_client.get(f'/realizations/projects/{slug}', query_string={'lang': language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    source = next(project for project in content.load_projects(language) if project['slug'] == slug)
    assert source['title'] in html
    assert source['summary'] in html
    for heading in re.findall(r'^## (.+)$', source['body'], flags=re.M):
        assert heading.replace('&', '&amp;') in html
    for image in source['images']:
        url = f'/realizations/static/images/{image["file"]}'
        rendered = ('ouverture' in image['emplacements'] or any(
            block.get('image', {}).get('id') == image['id']
            for section in content.case_sections(source) for block in section['blocks']))
        assert (url in html) is rendered
        assert admin_client.get(url).status_code == 200
        if rendered:
            assert image['legende'].replace('&', '&amp;') in html
    assert 'controle-prive' not in html
    assert 'prompt:' not in html
    assert '/Users/' not in html


def test_unreviewed_or_unknown_case_has_no_detail_route(admin_client):
    for slug in ['d01', 'd02', 'pp018', 'missing', '..%2F..%2FREADME']:
        assert admin_client.get(f'/realizations/projects/{slug}').status_code == 404


def test_markdown_edits_update_cards_and_case_without_restart(admin_client, tmp_path, monkeypatch):
    source = content.CONTENT_DIR / 'pp002.fr.md'
    post = frontmatter.load(source)
    post['display_version'] = 'long'
    post['title'] = 'Titre relu depuis Markdown'
    post['summary'] = 'Résumé modifié sans changer un template.'
    post['skills'] = ['agentic_ai']
    post['year'] = 2030
    post.content += '\n\n## Une section ajoutée\n\nUn nouveau paragraphe éditorial.\n'
    (tmp_path / source.name).write_text(frontmatter.dumps(post), encoding='utf-8')
    (tmp_path / 'skills.yml').write_text((content.CONTENT_DIR / 'skills.yml').read_text(), encoding='utf-8')
    monkeypatch.setattr(content, 'CONTENT_DIR', tmp_path)
    for path in ['/realizations/', '/realizations/projects/pp002']:
        html = admin_client.get(path).get_data(as_text=True)
        assert post['title'] in html
        assert post['summary'] in html
    catalogue = admin_client.get('/realizations/').get_data(as_text=True)
    assert 'data-skills="agentic_ai"' in catalogue
    assert 'data-year="2030"' in catalogue
    assert 'IA agentique' in catalogue
    html = admin_client.get('/realizations/projects/pp002').get_data(as_text=True)
    assert 'Une section ajoutée' in html
    assert 'Un nouveau paragraphe éditorial.' in html


def test_every_project_is_available_in_both_interfaces():
    for language in ['fr', 'en']:
        projects = content.load_projects(language)
        assert len(projects) == 84
        assert len({project['id'] for project in projects}) == 84
        for project in projects:
            assert project['title']
            assert isinstance(project['summary'], str)
            assert set(project['themes']) <= set(content.THEMES)
            assert project['origin'] in {'personal', 'professional'}


def test_shared_theme_fonts_are_available(admin_client):
    for font in ['EBGaramond-VariableFont_wght.ttf',
                 'EBGaramond-Italic-VariableFont_wght.ttf',
                 'Roboto-VariableFont_wght.ttf',
                 'Roboto-Italic-VariableFont_wght.ttf']:
        response = admin_client.get('/static/fonts/' + font)
        assert response.status_code == 200
        assert len(response.data) > 10000


@pytest.mark.parametrize('entry', ['/experiences_menu', '/experiences/'])
@pytest.mark.parametrize('language', ['fr', 'en'])
def test_existing_pro_pages_remain_the_main_entry(client, entry, language):
    html = client.get(entry, query_string={'lang': language}).get_data(as_text=True)
    assert 'ML &amp; AI' in html
    assert '/experiences/big_data' in html
    assert '/experiences/fablab' in html
    assert 'realizations-filters' not in html
    assert '/realizations/' not in html


@pytest.mark.parametrize('path', [
    '/realizations/', '/realizations/projects/pp001',
    '/realizations/projects/pp002',
    '/realizations/static/images/astronomy/jupiter.png',
    '/realizations/static/js/realizations.js',
])
def test_preview_requires_admin_session(client, admin_headers, path):
    assert client.get(path).status_code == 404
    assert client.get(path, headers=admin_headers).status_code == 404


def test_admin_has_preview_entry_and_session_expiry_revokes_access(admin_client):
    import time

    response = admin_client.get('/experiences_menu')
    assert '/realizations/' in response.get_data(as_text=True)
    response = admin_client.get('/realizations/')
    assert response.headers['Cache-Control'] == 'private, no-store'
    assert response.headers['X-Robots-Tag'] == 'noindex, nofollow'
    with admin_client.session_transaction() as session:
        session['admin_until'] = time.time() - 1
    assert admin_client.get('/realizations/').status_code == 404


def test_imported_case_uses_translated_english_source(admin_client):
    response = admin_client.get('/realizations/projects/p035', query_string={'lang': 'en'})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    source = next(project for project in content.load_projects('en') if project['slug'] == 'p035')
    assert 'French source text.' not in html
    assert 'Professional project · Case study' in html
    assert source['title'] in html


def test_imported_studies_have_visible_sections_and_local_media():
    projects = [p for p in content.load_projects('fr') if p['detail']]
    assert len(projects) == 80
    for project in projects:
        sections = content.case_sections(project)
        assert any(block.get('html') for section in sections for block in section['blocks'])
        placed = {block['image']['id'] for section in sections for block in section['blocks']
                  if 'image' in block}
        for image in project['images']:
            assert ('ouverture' in image['emplacements'] or image['id'] in placed
                    or ('galerie' in image['emplacements'] and image['file'].endswith('.svg')))
            assert (content.CONTENT_DIR.parents[3] / 'realizations/static/images' / image['file']).is_file()


def test_skill_metadata_and_years_support_the_future_map():
    import yaml

    registry = yaml.safe_load((content.CONTENT_DIR / 'skills.yml').read_text())
    for language in ('fr', 'en'):
        projects = content.load_projects(language)
        assert projects[-1]['id'] == 'PP020'
        for project in projects:
            assert 'tools' not in project
            assert project['skills']
            assert len(project['skills']) == len(set(project['skills']))
            assert set(project['skills']) <= set(registry)
            assert project['skill_labels'] == [registry[key][language] for key in project['skills']]
            assert project['year'] is None or type(project['year']) is int


@pytest.mark.parametrize('language,heading', [
    ('fr', 'Compétences mobilisées'), ('en', 'Skills used'),
])
def test_rust_case_has_translated_skills(admin_client, language, heading):
    projects = content.load_projects(language)
    project = next(item for item in projects if item['id'] == 'PP020')
    assert project['year'] == 2026
    response = admin_client.get('/realizations/projects/pp020', query_string={'lang': language})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert heading in html
    source = frontmatter.load(content.CONTENT_DIR / f'pp020.{language}.md')
    assert all(term in source.content for term in ('Rust', 'Codex', 'Ollama', 'OpenAI'))
    assert all(label in html for label in project['skill_labels'])


@pytest.mark.parametrize('language', ['fr', 'en'])
def test_display_tag_selects_short_content_without_long_text_or_images(admin_client, tmp_path, monkeypatch, language):
    import yaml

    (tmp_path / 'skills.yml').write_text((content.CONTENT_DIR / 'skills.yml').read_text())
    canonical = dict(id='PP900', title='PRIVATE LONG TITLE', summary='PRIVATE LONG SUMMARY',
                     origin='personal', themes=['apps'], skills=['software_development'],
                     year=2026, featured=False, detail=True, display_version='short',
                     related_ids=['PP901'], images=[{
                         'id': 'private', 'file': 'private-image.jpg',
                         'alt': 'PRIVATE ALT', 'legende': 'PRIVATE CAPTION',
                         'emplacements': ['ouverture'],
                     }])
    for lang in ['fr', 'en']:
        (tmp_path / f'case.{lang}.md').write_text(frontmatter.dumps(
            frontmatter.Post('# PRIVATE LONG TITLE\n\n## Private details\n\nPRIVATE LONG BODY', **canonical)))
        short = dict(id='PP900', title='Short title '+lang, summary='Short summary '+lang,
                     images=[], related_ids=[])
        (tmp_path / f'case.short.{lang}.md').write_text(frontmatter.dumps(
            frontmatter.Post('## Brief overview\n\nSelected short text '+lang, **short)))
    monkeypatch.setattr(content, 'CONTENT_DIR', tmp_path)
    for route in ['/realizations/', '/realizations/projects/case']:
        response = admin_client.get(route, query_string={'lang': language, 'version': 'long'})
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Short title '+language in html
        assert 'PRIVATE' not in html
        assert 'private-image.jpg' not in html
        assert 'data-display-version="short"' in html
    french = frontmatter.load(tmp_path / 'case.fr.md')
    french['display_version'] = 'long'
    (tmp_path / 'case.fr.md').write_text(frontmatter.dumps(french))
    html = admin_client.get('/realizations/projects/case', query_string={'lang': language}).get_data(as_text=True)
    assert 'PRIVATE LONG BODY' in html
    assert 'Selected short text' not in html


def test_missing_short_content_does_not_reveal_the_long_version(tmp_path, monkeypatch):
    (tmp_path / 'skills.yml').write_text('{}')
    post = frontmatter.Post('PRIVATE BODY', id='PP900', title='PRIVATE TITLE',
                            summary='', origin='personal', themes=['apps'], skills=[],
                            year=None, featured=False, detail=True, images=[],
                            display_version='short')
    (tmp_path / 'case.fr.md').write_text(frontmatter.dumps(post))
    monkeypatch.setattr(content, 'CONTENT_DIR', tmp_path)
    with pytest.raises(ValueError, match='missing short source'):
        content.load_projects('fr')


def test_all_projects_have_complete_long_and_short_language_sources():
    paths = [path for path in content.CONTENT_DIR.glob('*.fr.md') if '.short.' not in path.name]
    assert len(paths) == 84
    for path in paths:
        french = frontmatter.load(path)
        slug = path.name.removesuffix('.fr.md')
        english = frontmatter.load(content.CONTENT_DIR / (slug + '.en.md'))
        assert english['id'] == french['id']
        assert french['display_version'] in {'long', 'short'}
        assert len(english['images']) == len(french['images'])
        assert {image['file'] for image in english['images']} == {image['file'] for image in french['images']}
        for language in ('fr', 'en'):
            short = frontmatter.load(content.CONTENT_DIR / (slug + '.short.' + language + '.md'))
            assert short['title'] and short['summary']
            assert isinstance(short['images'], list)
            assert isinstance(short['related_ids'], list)
            assert len(short.content.split()) <= 300
        if french.content:
            assert len(english.content.split()) >= .72 * len(french.content.split())
            assert re.findall(r'^#{1,6}(?= )', english.content, flags=re.M) == re.findall(r'^#{1,6}(?= )', french.content, flags=re.M)



def test_introductory_paragraphs_before_first_section_are_preserved():
    project = dict(body="# Project\n\nIntroductory paragraph.\n\n## Results\n\nA result.",
                   images=[], language="en")
    sections = content.case_sections(project)
    assert "Introductory paragraph." in sections[0]["blocks"][0]["html"]
    assert sections[1]["title"] == "Results"


@pytest.mark.parametrize('language,title', [('fr', 'Galerie du projet'), ('en', 'Project gallery')])
@pytest.mark.parametrize('extra_file,visible', [
    (None, False), ('cover.jpg', False), ('references.svg', False), ('photo.jpg', True),
    ('illustration.webp', True),
])
def test_gallery_requires_a_distinct_additional_raster_image(language, title, extra_file, visible):
    images = [dict(id='cover', file='cover.jpg', emplacements=['ouverture'])]
    if extra_file:
        images.append(dict(id='extra', file=extra_file, emplacements=['galerie']))
    project = dict(language=language, images=images,
                   body=f'## Context\n\nProject context.\n\n## {title}\n\nGallery introduction.')
    sections = content.case_sections(project)
    assert any(section['title'] == title for section in sections) is visible
    assert sections[0]['title'] == 'Context'


@pytest.mark.parametrize('language', ['fr', 'en'])
def test_responsive_images_are_available_only_to_admin(admin_client, client, language):
    import json

    manifest = json.loads(content.IMAGE_MANIFEST.read_text())
    project = next(p for p in content.load_projects(language) if p['id'] == 'PP020')
    image = project['images'][0]
    variants = manifest[image['file']]['variants']
    assert [variant['width'] for variant in variants] == [320, 640, 960, 1440]
    url = '/realizations/static/images/' + variants[1]['file']
    # Separate unauthenticated client must not receive a private thumbnail.
    with admin_client.application.test_client() as public:
        assert public.get(url).status_code == 404
    response = admin_client.get(url)
    assert response.status_code == 200
    assert response.mimetype == 'image/webp'
    html = admin_client.get('/realizations/', query_string={'lang': language}).get_data(as_text=True)
    assert 'type="image/webp"' in html
    assert url in html
    assert 'decoding="async"' in html
    assert '960w' in html
    assert '1440w' not in html  # Cards never request full-size detail variants.
