"""Small, dependency-free guards for administrative write endpoints."""

from __future__ import annotations

from functools import wraps
from hmac import compare_digest

from flask import abort, current_app, request


def enforce_admin_api_token() -> None:
    """Require the configured token for persistent API writes in production."""
    if not current_app.config.get("REQUIRE_ADMIN_API_TOKEN", False):
        return

    expected = current_app.config.get("ADMIN_API_TOKEN")
    provided = request.headers.get("X-Admin-Token", "")
    if not expected:
        current_app.logger.error("Persistent API write refused: ADMIN_API_TOKEN is not configured")
        abort(503, description="Les écritures administratives ne sont pas configurées.")
    if not compare_digest(provided, expected):
        abort(403, description="Autorisation administrateur requise.")


def require_admin_api_token(view):
    """Decorator for endpoints that persist shared data."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        enforce_admin_api_token()
        return view(*args, **kwargs)

    return wrapped
