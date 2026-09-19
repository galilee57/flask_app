"""Explicit, idempotent import of old local files; sources are never changed."""
import json
from pathlib import Path
import click
from app.extensions import db
from app.storage.runtime_models import Todo, SavedPattern
from app.projects.todolist.repository import TodoRepository
from app.projects.game_of_life.routes import _safe_name


def register_storage_import(app):
    @app.cli.command("storage-import")
    @click.option("--todos", type=click.Path(exists=True, path_type=Path))
    @click.option("--patterns", type=click.Path(exists=True, file_okay=False, path_type=Path))
    def import_storage(todos, patterns):
        """Import old Todo JSON and pattern directory, skipping existing keys."""
        count = 0
        try:
            if todos:
                for task in TodoRepository(todos).list():
                    if not isinstance(task.get("id"), str) or len(task["id"]) > 36:
                        raise ValueError("Identifiant Todo invalide")
                    if not isinstance(task.get("text"), str) or not isinstance(task.get("done"), bool):
                        raise ValueError("Tâche Todo invalide")
                    if not isinstance(task.get("created_at"), str) or len(task["created_at"]) > 40:
                        raise ValueError("Date Todo invalide")
                    if db.session.get(Todo, task["id"]) is None:
                        db.session.add(Todo(**{key: task[key] for key in ("id", "text", "done", "created_at")}))
                        count += 1
            if patterns:
                for path in sorted(patterns.glob("*.json")):
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    name = _safe_name(path.stem)
                    if not isinstance(payload.get("grid"), list):
                        raise ValueError(f"Motif invalide: {path.name}")
                    if db.session.get(SavedPattern, name) is None:
                        db.session.add(SavedPattern(name=name, payload=payload))
                        count += 1
            db.session.commit()
        except (ValueError, RuntimeError, KeyError) as exc:
            db.session.rollback()
            raise click.ClickException(str(exc)) from exc
        click.echo(f"{count} éléments importés")
