# Repository Guidelines

## Project Structure & Module Organization

The Flask application factory is in `app/__init__.py`; `wsgi.py` and `run.py` are entry points. Shared configuration, extensions, security helpers, and blueprint registration live directly under `app/`. Feature code is organized as blueprints in `app/projects/<project_name>/`, while portfolio pages are in `app/main/` and `app/experiences/`. Keep templates and static assets beside the blueprint that owns them. Bilingual FlatPages content uses paired `.fr.md` and `.en.md` files under `app/main/content/docs/`. Database migrations belong in `migrations/`; automated tests belong in `tests/`.

## Build, Test, and Development Commands

- `python3 -m venv .venv && source .venv/bin/activate` creates and activates a local environment.
- `pip install -r requirements.txt` installs Flask, database, content, and test dependencies.
- `FLASK_CONFIG=development flask --app wsgi --debug run` starts the development server with reload and debugging.
- `pytest` runs the suite configured by `pytest.ini`; use `pytest tests/test_security_and_api.py -q` for a focused check.
- `flask --app wsgi db upgrade` applies Alembic migrations.
- `npx @tailwindcss/cli -i input.css -o app/main/static/css/output.css --watch` rebuilds Tailwind CSS during UI work.

## Coding Style & Naming Conventions

Use four-space indentation and PEP 8 conventions for Python. Name modules, functions, fixtures, and blueprint directories with `snake_case`; use `PascalCase` for classes. Keep routes thin and place persistence or reusable logic in models/helpers. Follow the existing Jinja formatting and keep project assets under `static/css`, `static/js`, or `static/images`. No formatter is enforced, so avoid unrelated reformatting.

## Testing Guidelines

Tests use Pytest and Flask's test client. Name files `test_*.py` and tests `test_<behavior>`. Add regression coverage for changed routes, authorization, persistence, and response contracts. Use the `testing` app configuration and fixtures from `tests/conftest.py`; tests must not depend on production data or network access.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Harden production configuration and persistence APIs`. Keep each commit focused. Pull requests should explain behavior changes, list validation commands, link relevant issues, and include screenshots for template or CSS changes. Call out migrations, environment-variable changes, and API compatibility impacts.

## Security & Agent Instructions

Never commit `.env`, tokens, private keys, or production databases. Production writes require `X-Admin-Token`; preserve that boundary. Deploy only through the documented `staging` workflow. Never use `rm -rf`; move disposable files to Trash with `trash <path>` so they remain recoverable.
