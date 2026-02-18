import os
import pytest
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


def test_settings_load_from_explicit_env_file(tmp_path):
    env_file = tmp_path / ".env.test"
    env_file.write_text("LOG_LEVEL=WARNING\nOCR_DPI=150\n")
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings.load(env_path=str(env_file))
        assert settings.log_level == "WARNING"
        assert settings.ocr_dpi == 150


def test_settings_max_workers_from_env():
    with patch.dict(os.environ, {"MAX_WORKERS": "4"}, clear=True):
        settings = Settings.load()
        assert settings.max_workers == 4


def test_settings_immutability():
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings.load()
        import dataclasses
        with pytest.raises(dataclasses.FrozenInstanceError):
            settings.log_level = "CRITICAL"


def test_default_paths_contain_data_dir():
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings.load()
        assert "data" in settings.input_dir
        assert "data" in settings.output_dir
