import os
from unittest.mock import patch

from src.core.config.settings import Settings


def test_settings_load_defaults():
    # Clear env vars to test defaults
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings.load()
        assert settings.log_level == "INFO"
        assert settings.ocr_dpi == 300
        assert settings.ocr_language == "eng"
        assert "tesseract" in settings.tesseract_path.lower()


def test_settings_load_from_env():
    # Set env vars to test loading
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "OCR_DPI": "600",
        "OCR_LANGUAGE": "deu",
        "TESSERACT_PATH": "/usr/bin/tesseract",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings.load()
        assert settings.log_level == "DEBUG"
        assert settings.ocr_dpi == 600
        assert settings.ocr_language == "deu"
        assert settings.tesseract_path == "/usr/bin/tesseract"
