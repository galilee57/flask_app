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
def test_cli_posts_to_configured_provider(app, monkeypatch, provider):
    app.config.update(
        LLM_PROVIDER=provider, LLM_LOCAL_BASE_URL="http://127.0.0.1:8081/v1",
        OPENAI_API_KEY="secret", OPENAI_MODEL="test-model",
    )
    post = Mock()
    post.return_value.json.return_value = {"choices": [{"message": {"content": "<b>Hello</b>"}}]}
    monkeypatch.setattr("requests.post", post)
    result = app.test_cli_runner().invoke(args=["llm-prompt", "Hello"])
    assert result.exit_code == 0
    assert "<b>Hello</b>" in result.output
    assert "secret" not in result.output
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


def test_admin_rag_uses_retrieved_context_and_renders_sources(app, signed_in, tmp_path, monkeypatch):
    import json

    from app.core.rag import EMBEDDING_MODEL, INDEX_VERSION

    index = tmp_path / "projects.json"
    index.write_text(json.dumps({"version": INDEX_VERSION, "model": EMBEDDING_MODEL, "chunks": [{
        "id": "case:benchmark:fr:1", "project_id": "P001", "slug": "benchmark",
        "title": "Benchmark", "section": "Contexte", "text": "<extrait privé>",
        "language": "fr", "source": "case", "embedding": [1, 0],
    }]}), encoding="utf-8")
    app.config.update(LLM_PROVIDER="local", RAG_INDEX_PATH=index)
    signed_in.get("/admin/llm?lang=fr")
    with signed_in.session_transaction() as session:
        csrf = session["admin_csrf"]
    embedding_response = Mock()
    embedding_response.json.return_value = {"data": [{"index": 0, "embedding": [1, 0]}]}
    chat_response = Mock()
    chat_response.json.return_value = {"choices": [{"message": {"content": "Réponse [1]"}}]}
    post = Mock(side_effect=[embedding_response, chat_response])
    monkeypatch.setattr("requests.post", post)

    response = signed_in.post("/admin/llm", data={
        "prompt": "Quel benchmark ?", "use_rag": "on", "csrf_token": csrf,
    })
    assert response.status_code == 200
    assert b"P001" in response.data
    assert b"&lt;extrait priv\xc3\xa9&gt;" in response.data
    assert b"/realizations/projects/benchmark" in response.data
    messages = post.call_args.kwargs["json"]["messages"]
    assert "[1] Benchmark" in messages[-1]["content"]
    assert "<extrait privé>" in messages[-1]["content"]
    assert post.call_args_list[0].args[0].endswith("/embeddings")


def test_rag_rebuild_requires_dev_admin_and_csrf(app, client, signed_in, monkeypatch):
    start = Mock()
    monkeypatch.setattr("app.core.admin.start_rag_rebuild", start)
    app.config["ENV"] = "production"
    assert signed_in.post("/admin/llm/rebuild").status_code == 404
    app.config["ENV"] = "development"
    assert app.test_client().post("/admin/llm/rebuild").status_code == 403
    assert signed_in.post("/admin/llm/rebuild").status_code == 400
    with signed_in.session_transaction() as session:
        session["admin_csrf"] = "rebuild"
    assert signed_in.post("/admin/llm/rebuild", data={"csrf_token": "rebuild"}).status_code == 303
    start.assert_called_once()


def test_admin_shows_partial_answer_when_model_reaches_limit(app, signed_in, monkeypatch):
    app.config["LLM_PROVIDER"] = "local"
    monkeypatch.setattr("app.core.admin.load_portfolio_summary", lambda _: {
        "total": 1, "tagged": 0, "skills": [],
    })
    post = Mock()
    post.return_value.json.return_value = {
        "choices": [{"message": {"content": "Réponse partielle"}, "finish_reason": "length"}],
    }
    monkeypatch.setattr("requests.post", post)
    signed_in.get("/admin/llm?lang=en")
    with signed_in.session_transaction() as session:
        token = session["admin_csrf"]
    response = signed_in.post("/admin/llm", data={"mode": "summary", "prompt": "Question", "csrf_token": token})
    assert b"generation limit" in response.data
    assert b"partielle" in response.data
    assert post.call_args.kwargs["json"]["max_completion_tokens"] == 1024


def test_admin_renders_markdown_without_active_model_html(app, signed_in, monkeypatch):
    app.config["LLM_PROVIDER"] = "local"
    monkeypatch.setattr("app.core.admin.load_portfolio_summary", lambda _: {
        "total": 1, "tagged": 0, "skills": [],
    })
    post = Mock()
    post.return_value.json.return_value = {"choices": [{"message": {"content": (
        "## Titre\n\n- **Gras**\n- [Danger](javascript:alert%281%29)\n\n"
        "<script>alert(1)</script>\n\n![Image](https://example.com/image.png)"
    )}}]}
    monkeypatch.setattr("requests.post", post)
    signed_in.get("/admin/llm")
    with signed_in.session_transaction() as session:
        token = session["admin_csrf"]
    response = signed_in.post("/admin/llm", data={"mode": "summary", "prompt": "Question", "csrf_token": token})
    assert b"<h2>Titre</h2>" in response.data
    assert b"<li><strong>Gras</strong></li>" in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data
    assert b"javascript:alert" not in response.data
    assert b"https://example.com/image.png" not in response.data


def test_admin_skills_summary_uses_snapshot_without_embedding_query(app, signed_in, tmp_path, monkeypatch):
    import json

    index = tmp_path / "projects.json"
    index.write_text(json.dumps({"summary": {
        "total": 10, "tagged": 6,
        "skills": {"en": [{"label": "Python", "count": 6, "examples": [{
            "project_id": "P006", "slug": "example", "title": "Example", "source": "case",
        }]}]},
    }}), encoding="utf-8")
    app.config.update(LLM_PROVIDER="local", RAG_INDEX_PATH=index)
    post = Mock()
    post.return_value.json.return_value = {"choices": [{"message": {"content": "**Python**"}}]}
    monkeypatch.setattr("requests.post", post)
    page = signed_in.get("/admin/llm?lang=en&summary=skills")
    assert b"6 of 10 project sheets" in page.data
    assert b"/realizations/projects/example" in page.data
    post.assert_not_called()

    with signed_in.session_transaction() as session:
        csrf = session["admin_csrf"]
    page = signed_in.post("/admin/llm", data={
        "csrf_token": csrf, "mode": "summary", "prompt": "What are the main skills?",
    })
    assert page.status_code == 200
    assert b"<strong>Python</strong>" in page.data
    post.assert_called_once()
    facts = post.call_args.kwargs["json"]["messages"][-1]["content"]
    assert "6 of 10" in facts and "Python: 6 projects (examples: P006)" in facts


def test_admin_rejects_direct_chat_mode(app, signed_in, monkeypatch):
    post = Mock()
    monkeypatch.setattr("requests.post", post)
    with signed_in.session_transaction() as session:
        session["admin_csrf"] = "test-mode"
    response = signed_in.post("/admin/llm", data={
        "mode": "direct", "prompt": "Hello", "csrf_token": "test-mode",
    })
    assert response.status_code == 400
    post.assert_not_called()


def test_admin_compares_offer_with_portfolio_evidence(app, signed_in, tmp_path, monkeypatch):
    import json

    from app.core.rag import EMBEDDING_MODEL, INDEX_VERSION

    index = tmp_path / "projects.json"
    rows = [
        {
            "project_id": "P1", "slug": "analytics", "source": "case",
            "title": "Dashboard", "section": "Results", "language": "en",
            "text": "Built a dashboard", "embedding": [1, 0], "skills": ["Python"],
        },
        {
            "project_id": "P2", "slug": "training", "source": "case",
            "title": "Training", "section": "Results", "language": "en",
            "text": "Trained operators", "embedding": [0, 1], "skills": ["Training"],
        },
    ]
    index.write_text(json.dumps({"version": INDEX_VERSION, "model": EMBEDDING_MODEL, "chunks": rows}))
    app.config.update(LLM_PROVIDER="local", RAG_INDEX_PATH=index)
    signed_in.get("/admin/llm?lang=en")
    with signed_in.session_transaction() as session:
        token = session["admin_csrf"]
    embeddings = Mock()
    embeddings.json.return_value = {"data": [
        {"index": 0, "embedding": [1, 0]}, {"index": 1, "embedding": [0, 1]},
    ]}
    completion = Mock()
    completion.json.return_value = {"choices": [{"message": {"content": "Python [1]; training [2]."}}]}
    post = Mock(side_effect=[embeddings, completion])
    monkeypatch.setattr("requests.post", post)
    response = signed_in.post("/admin/llm", data={
        "mode": "offer", "csrf_token": token,
        "prompt": "Build dashboards with Python.\n\nTrain operators.",
    })
    assert response.status_code == 200
    assert b"/realizations/projects/analytics" in response.data
    assert b"/realizations/projects/training" in response.data
    messages = post.call_args.kwargs["json"]["messages"]
    assert "Built a dashboard" in messages[-1]["content"]
    assert "Python" in messages[-1]["content"]
    assert "Trained operators" in messages[-1]["content"]
