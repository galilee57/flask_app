from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, update, delete
from app.extensions import db
from app.storage.runtime_models import Todo
from .services import TodoNotFoundError


class SQLTodoService:
    def list(self):
        return [task.to_dict() for task in db.session.scalars(
            select(Todo).order_by(Todo.created_at, Todo.id))]

    def create(self, command):
        task = Todo(id=str(uuid4()), text=command.text, done=False,
                    created_at=datetime.now(timezone.utc).isoformat())
        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    def update(self, task_id, command):
        values = {key: value for key, value in {"text": command.text, "done": command.done}.items()
                  if value is not None}
        if values:
            result = db.session.execute(update(Todo).where(Todo.id == task_id).values(**values))
            if result.rowcount != 1:
                db.session.rollback()
                raise TodoNotFoundError(task_id)
        task = db.session.get(Todo, task_id)
        if task is None:
            raise TodoNotFoundError(task_id)
        db.session.commit()
        return task.to_dict()

    def delete(self, task_id):
        result = db.session.execute(delete(Todo).where(Todo.id == task_id))
        if result.rowcount != 1:
            db.session.rollback()
            raise TodoNotFoundError(task_id)
        db.session.commit()
