"""Todo use cases independent from Flask and filesystem details."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .repository import TodoRepository
from .schemas import CreateTodo, UpdateTodo


class TodoNotFoundError(LookupError):
    """Raised when an operation targets an unknown task."""


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    def list(self) -> list[dict[str, Any]]:
        return self.repository.list()

    def create(self, command: CreateTodo) -> dict[str, Any]:
        tasks = self.repository.list()
        task = {
            "id": str(uuid4()),
            "text": command.text,
            "done": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        tasks.append(task)
        self.repository.save(tasks)
        return task

    def update(self, task_id: str, command: UpdateTodo) -> dict[str, Any]:
        tasks = self.repository.list()
        for task in tasks:
            if task.get("id") == task_id:
                if command.text is not None:
                    task["text"] = command.text
                if command.done is not None:
                    task["done"] = command.done
                self.repository.save(tasks)
                return task
        raise TodoNotFoundError(task_id)

    def delete(self, task_id: str) -> None:
        tasks = self.repository.list()
        updated_tasks = [task for task in tasks if task.get("id") != task_id]
        if len(updated_tasks) == len(tasks):
            raise TodoNotFoundError(task_id)
        self.repository.save(updated_tasks)
