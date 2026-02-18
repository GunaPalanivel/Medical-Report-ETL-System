from src.core import Settings, configure_logging


def test_settings_loads_defaults():
    settings = Settings.load()
    assert settings.ocr_dpi == 300
    assert settings.input_dir


def test_configure_logging_returns_logger():
    logger = configure_logging("INFO")
    assert logger.name == "medical_report_etl"
