"""Validation at the Todo HTTP boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class TodoValidationError(ValueError):
    """Raised when a Todo API payload does not match its contract."""


@dataclass(frozen=True)
class CreateTodo:
    text: str


@dataclass(frozen=True)
class UpdateTodo:
    text: str | None = None
    done: bool | None = None


def _validated_text(value: Any) -> str:
    if not isinstance(value, str) or not (text := value.strip()) or len(text) > 500:
        raise TodoValidationError("Le champ 'text' est requis et limité à 500 caractères.")
    return text


def parse_create_todo(payload: Any) -> CreateTodo:
    if not isinstance(payload, dict):
        raise TodoValidationError("Un objet JSON est requis.")
    return CreateTodo(text=_validated_text(payload.get("text", payload.get("task"))))


def parse_update_todo(payload: Any) -> UpdateTodo:
    if not isinstance(payload, dict):
        raise TodoValidationError("Un objet JSON est requis.")
    if not payload:
        raise TodoValidationError("Au moins un champ à modifier est requis.")

    text = None
    done = None
    if "text" in payload:
        text = _validated_text(payload["text"])
    if "done" in payload:
        if not isinstance(payload["done"], bool):
            raise TodoValidationError("Le champ 'done' doit être booléen.")
        done = payload["done"]
    if text is None and done is None:
        raise TodoValidationError("Les champs autorisés sont 'text' et 'done'.")
    return UpdateTodo(text=text, done=done)
