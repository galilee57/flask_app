import pytest

from app.config import ProdConfig, TestingConfig, get_config


def test_unspecified_config_defaults_to_production(monkeypatch):
    monkeypatch.delenv("FLASK_CONFIG", raising=False)
    assert get_config() is ProdConfig


def test_unknown_config_is_rejected(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "preview")
    with pytest.raises(ValueError, match="inconnue"):
        get_config()


def test_testing_config_has_secure_defaults_for_api_tests():
    assert TestingConfig.MAX_CONTENT_LENGTH == 1 * 1024 * 1024
    assert TestingConfig.SESSION_COOKIE_HTTPONLY is True
    assert TestingConfig.SESSION_COOKIE_SAMESITE == "Lax"
    assert ProdConfig.SESSION_COOKIE_SECURE is True
