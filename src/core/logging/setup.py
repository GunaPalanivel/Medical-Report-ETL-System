import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .formatters import JSONFormatter, DetailedFormatter


def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Configure a root logger with console and optional file handlers."""
    logger = logging.getLogger("medical_report_etl")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(DetailedFormatter())
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger
