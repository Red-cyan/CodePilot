from app.core.config import Settings


def test_settings_reads_deepseek_environment_names(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-test")

    settings = Settings()

    assert settings.deepseek_api_key == "test-key"
    assert settings.deepseek_base_url == "https://example.com"
    assert settings.deepseek_model == "deepseek-test"
