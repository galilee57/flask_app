from . import bp
from flask import render_template, jsonify, current_app, request
from pathlib import Path
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime
import json


def _tasks_file() -> Path:
    root = Path(current_app.root_path)
    data_dir = root / "projects" / "todolist" / "static" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Data directory: {data_dir}")
    return data_dir / "todolist.json"


def load_tasks() -> List[Dict[str, Any]]:
    path = _tasks_file()
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        try:
            bad_path = path.with_suffix(path.suffix + ".bad")
            if path.exists():
                path.rename(bad_path)
        except Exception:
            pass
        return []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Écriture atomique pour éviter les fichiers corrompus."""
    path = _tasks_file()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic move sur OS modernes


@bp.get("/")
def home():
    return render_template("index_todolist.html")


@bp.get("/api/todolist")
def get_todos():
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    print(_tasks_file())
    return jsonify(tasks), 200


@bp.post("/api/todolist")
def create_todo():
    """
    Body JSON attendu: {"text": "..."} (ou "task": "...")
    Réponse: la tâche créée (201).
    """
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or payload.get("task") or "").strip()
    if not text:
        return jsonify({"error": "Le champ 'text' est requis."}), 400

    tasks = load_tasks()
    new_task = {
        "id": str(uuid4()),
        "text": text,
        "done": False,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@bp.delete("/api/todolist/<task_id>")
def delete_todo(task_id):
    """
    Supprime une tâche par son ID.
    Réponse: 204 si succès, 404 si la tâche n'existe pas.
    """
    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["id"] != task_id]
    if len(updated_tasks) == len(tasks):
        return jsonify({"error": "Tâche non trouvée."}), 404

    save_tasks(updated_tasks)
    return '', 204

@bp.put("/api/todolist/<task_id>")
def update_todo(task_id):
    """
    Met à jour une tâche par son ID.
    Body JSON attendu: {"text": "...", "done": true/false}
    Réponse: la tâche mise à jour (200) ou 404 si la tâche n'existe pas.
    """
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    done = payload.get("done")

    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if text is not None:
                task["text"] = text.strip()
            if isinstance(done, bool):
                task["done"] = done
            save_tasks(tasks)
            return jsonify(task), 200

    return jsonify({"error": "Tâche non trouvée."}), 404