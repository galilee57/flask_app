"""Durable, atomic storage for Todo records."""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any


class TodoRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = RLock()

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                return []
            except json.JSONDecodeError as exc:
                raise RuntimeError("Le stockage des tâches est corrompu.") from exc
            if not isinstance(payload, list):
                raise RuntimeError("Le stockage des tâches est invalide.")
            return payload

    def save(self, tasks: list[dict[str, Any]]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary_path.write_text(
                json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            temporary_path.replace(self.path)
