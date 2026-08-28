from . import bp
from app.security import require_admin_api_token
from flask import current_app, render_template, jsonify, request
from pathlib import Path
from .repository import TodoRepository
from .schemas import TodoValidationError, parse_create_todo, parse_update_todo
from .services import TodoNotFoundError, TodoService


def _todo_service() -> TodoService:
    configured_path = current_app.config.get("TODOLIST_DATA_PATH")
    path = Path(configured_path) if configured_path else Path(current_app.instance_path) / "data" / "todolist.json"
    repositories = current_app.extensions.setdefault("todo_repositories", {})
    repository = repositories.setdefault(path, TodoRepository(path))
    return TodoService(repository)


@bp.get("/")
def home():
    return render_template("index_todolist.html")


@bp.get("/api/todolist")
def get_todos():
    return jsonify(_todo_service().list()), 200


@bp.post("/api/todolist")
@require_admin_api_token
def create_todo():
    """
    Body JSON attendu: {"text": "..."} (ou "task": "...")
    Réponse: la tâche créée (201).
    """
    try:
        task = _todo_service().create(parse_create_todo(request.get_json(silent=True)))
    except TodoValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(task), 201

@bp.delete("/api/todolist/<task_id>")
@require_admin_api_token
def delete_todo(task_id):
    """
    Supprime une tâche par son ID.
    Réponse: 204 si succès, 404 si la tâche n'existe pas.
    """
    try:
        _todo_service().delete(task_id)
    except TodoNotFoundError:
        return jsonify({"error": "Tâche non trouvée."}), 404
    return '', 204

@bp.put("/api/todolist/<task_id>")
@require_admin_api_token
def update_todo(task_id):
    """
    Met à jour une tâche par son ID.
    Body JSON attendu: {"text": "...", "done": true/false}
    Réponse: la tâche mise à jour (200) ou 404 si la tâche n'existe pas.
    """
    try:
        task = _todo_service().update(task_id, parse_update_todo(request.get_json(silent=True)))
    except TodoValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except TodoNotFoundError:
        return jsonify({"error": "Tâche non trouvée."}), 404
    return jsonify(task), 200
