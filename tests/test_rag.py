import numpy as np

from app.core.rag import answer_from_projects, chunk_sections, rank_passages


def test_chunk_sections_preserves_text_and_section():
    text = "x" * 1500
    chunks = list(chunk_sections("# Project\n\n## Approach\n" + text))
    assert len(chunks) == 2
    assert all(section == "Approach" and len(part) <= 1000 for section, part in chunks)
    assert "".join(part for _, part in chunks) == text


def test_rank_passages_uses_cosine_and_language():
    passages = [{"language": language} for language in ("fr", "en", "fr")]
    matrix = np.array([[3, 4], [1, 0], [1, 0]])
    ranked = rank_passages(passages, matrix, np.array([2, 0]), "fr")
    assert [record for record, _ in ranked] == [passages[2], passages[0]]


def test_missing_index_does_not_contact_a_provider(app, monkeypatch, tmp_path):
    app.config["RAG_INDEX_PATH"] = tmp_path / "absent.json"
    with app.app_context():
        import pytest
        from app.core.rag import RagError

        with pytest.raises(RagError, match="index"):
            answer_from_projects("Question", "fr")


def test_portfolio_summary_counts_projects_once_and_tracks_untagged():
    from app.core.rag import portfolio_summary

    common = {"slug": "example", "source": "case", "title": "Example"}
    documents = [
        dict(common, project_id="P1", language="fr", skills={"python": "Python"}),
        dict(common, project_id="P1", language="en", skills={"python": "Python"}),
        dict(common, project_id="P2", language="fr", skills={"python": "Python"}),
        dict(common, project_id="lab", language="en", source="lab", skills={}),
    ]
    summary = portfolio_summary(documents)
    assert summary["total"] == 3
    assert summary["tagged"] == 2
    assert summary["skills"]["fr"][0]["count"] == 2
    assert summary["skills"]["en"][0]["count"] == 2
    assert [p["project_id"] for p in summary["skills"]["en"][0]["examples"]] == ["P1", "P2"]


def test_training_and_employment_metadata_is_indexed(app):
    from app.core.rag import portfolio_documents, project_passages

    with app.app_context():
        documents = list(portfolio_documents())
        for language in ("fr", "en"):
            for project_id, kind in (
                ("F001", "education"), ("F002", "education"), ("P030", "experience"),
            ):
                document = next(row for row in documents
                                if row["project_id"] == project_id and row["language"] == language)
                chunks = list(project_passages(document))
                assert chunks and all(chunk["kind"] == kind for chunk in chunks)


def test_openai_embeddings_use_openai_endpoint_and_project_key(app, monkeypatch):
    from unittest.mock import Mock

    from app.core.rag import embed

    app.config.update(RAG_EMBEDDING_PROVIDER="openai", OPENAI_API_KEY="test-key")
    post = Mock()
    post.return_value.json.return_value = {"data": [{"index": 0, "embedding": [3, 4]}]}
    monkeypatch.setattr("requests.post", post)
    with app.app_context():
        assert np.allclose(embed(["Example"]), [[0.6, 0.8]])
    assert post.call_args.args[0] == "https://api.openai.com/v1/embeddings"
    assert post.call_args.kwargs["json"]["model"] == "text-embedding-3-small"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer test-key"


def test_build_if_stale_reuses_index_and_rebuilds_when_document_changes(app, tmp_path, monkeypatch):
    from unittest.mock import Mock

    from app.core.rag import build_index

    document = {
        "project_id": "P1", "slug": "demo", "title": "Demo", "language": "en",
        "source": "case", "summary": "", "body": "Initial", "skills": {},
        "kind": "project", "kind_label": "Project",
    }
    app.config["RAG_INDEX_PATH"] = tmp_path / "index.json"
    monkeypatch.setattr("app.core.rag.portfolio_documents", lambda: [document])
    embed = Mock(return_value=np.array([[1, 0]], dtype=np.float32))
    monkeypatch.setattr("app.core.rag.embed", embed)
    with app.app_context():
        build_index(if_stale=True)
        build_index(if_stale=True)
        embed.assert_called_once()
        document["body"] = "Edited"
        build_index(if_stale=True)
        assert embed.call_count == 2
        assert "Edited" in app.config["RAG_INDEX_PATH"].read_text()
