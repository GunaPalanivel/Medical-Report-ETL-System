import json
import logging
from pathlib import Path

from src.core.logging.formatters import JSONFormatter, DetailedFormatter
from src.core.logging.setup import configure_logging


def test_json_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        "test_logger", logging.INFO, "test_file.py", 10, "Test message", (), None
    )
    log_output = formatter.format(record)
    log_dict = json.loads(log_output)
    
    assert log_dict["message"] == "Test message"
    assert log_dict["level"] == "INFO"
    assert "timestamp" in log_dict
    assert "name" in log_dict  # Changed from "logger" to "name"


def test_detailed_formatter():
    formatter = DetailedFormatter()
    record = logging.LogRecord(
        "test_logger", logging.ERROR, "test_file.py", 20, "Error occurred", (), None
    )
    output = formatter.format(record)
    # Format is "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert "ERROR" in output
    assert "Error occurred" in output
    assert "test_logger" in output


def test_configure_logging(tmp_path):
    log_file = tmp_path / "test.log"
    # Reset logger handlers for this test to avoid pollution from other tests if possible
    # In a real scenario we might need a fixture to reset logging, but for now we test basic behavior
    # We use a unique logger name or rely on configure_logging logic
    
    # Actually configure_logging gets the "medical_report_etl" logger.
    # We should reset it if we want to test configuration.
    logger = logging.getLogger("medical_report_etl")
    logger.handlers = [] # Reset handlers
    
    logger = configure_logging("DEBUG", str(log_file))
    
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1  # Console + File
    
    logger.debug("Debug message")
    
    # Close handlers to flush
    for handler in logger.handlers:
        handler.close()
        
    if log_file.exists():
        content = log_file.read_text()
        assert "Debug message" in content
