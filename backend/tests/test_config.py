import os
from src.config import Settings

def test_config_loading():
    """Test that configuration is loaded correctly from environment variables."""
    # Test default configuration values
    settings = Settings()

    assert settings.environment == "development"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.debug is True
    assert settings.log_level == "info"
    assert settings.allowed_origins == "*"

def test_allowed_origins_list_property():
    """Test that allowed_origins_list property works correctly."""
    # Test wildcard case
    os.environ["ALLOWED_ORIGINS"] = "*"
    settings = Settings()
    assert settings.allowed_origins_list == ["*"]

    # Test multiple origins
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000, http://localhost:8080, https://example.com"
    settings = Settings()
    expected = ["http://localhost:3000", "http://localhost:8080", "https://example.com"]
    assert settings.allowed_origins_list == expected

    # Test single origin
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
    settings = Settings()
    assert settings.allowed_origins_list == ["http://localhost:3000"]

    # Clean up environment
    if "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]

def test_config_with_env_vars():
    """Test configuration with environment variables."""
    # Set some environment variables
    original_env = os.environ.copy()

    try:
        os.environ["ENVIRONMENT"] = "production"
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "9000"
        os.environ["DEBUG"] = "False"
        os.environ["LOG_LEVEL"] = "warning"

        settings = Settings()

        assert settings.environment == "production"
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000
        assert settings.debug is False
        assert settings.log_level == "warning"

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)