from unittest.mock import Mock

import pytest
import requests
from werkzeug.security import generate_password_hash


@pytest.fixture
def signed_in(app, client):
    app.config.update(ADMIN_USERNAME="admin", ADMIN_PASSWORD_HASH=generate_password_hash("test"))
    with client.session_transaction() as session:
        session["admin_csrf"] = "login"
    response = client.post("/admin", data={
        "username": "admin", "password": "test", "csrf_token": "login",
    })
    assert response.status_code == 302
    return client


def test_prompt_requires_admin_session(client, admin_headers):
    assert client.get("/admin/llm").status_code == 302
    assert client.post("/admin/llm", headers=admin_headers).status_code == 403


def test_prompt_requires_csrf(signed_in):
    assert signed_in.post("/admin/llm", data={"prompt": "Hello"}).status_code == 400


@pytest.mark.parametrize("provider", ["local", "openai"])
def test_prompt_posts_to_configured_provider(app, signed_in, monkeypatch, provider):
    app.config.update(
        LLM_PROVIDER=provider, LLM_LOCAL_BASE_URL="http://127.0.0.1:8081/v1",
        OPENAI_API_KEY="secret", OPENAI_MODEL="test-model",
    )
    post = Mock()
    post.return_value.json.return_value = {"choices": [{"message": {"content": "<b>Hello</b>"}}]}
    monkeypatch.setattr("requests.post", post)
    assert signed_in.get("/admin/llm?lang=en").status_code == 200
    with signed_in.session_transaction() as session:
        csrf_token = session["admin_csrf"]
    response = signed_in.post("/admin/llm", data={"prompt": "Hello", "csrf_token": csrf_token})
    assert response.status_code == 200
    assert b"&lt;b&gt;Hello&lt;/b&gt;" in response.data
    assert b"secret" not in response.data
    assert post.call_count == 1
    assert post.call_args.args[0] == {
        "local": "http://127.0.0.1:8081/v1/chat/completions",
        "openai": "https://api.openai.com/v1/chat/completions",
    }[provider]
    assert post.call_args.kwargs["headers"].get("Authorization") == (
        "Bearer secret" if provider == "openai" else None
    )


def test_cli_reports_local_failure_without_falling_back(app, monkeypatch):
    app.config.update(
        LLM_PROVIDER="local", LLM_LOCAL_BASE_URL="http://127.0.0.1:8081/v1",
        OPENAI_API_KEY="secret", OPENAI_MODEL="test-model",
    )
    post = Mock(side_effect=requests.Timeout("private upstream details"))
    monkeypatch.setattr("requests.post", post)
    result = app.test_cli_runner().invoke(args=["llm-prompt", "Hello"])
    assert result.exit_code == 1
    assert "unavailable" in result.output
    assert "private upstream details" not in result.output
    assert post.call_count == 1
    assert post.call_args.args[0] == "http://127.0.0.1:8081/v1/chat/completions"
