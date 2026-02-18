import pytest
from src.features.ocr.validators import validate_ocr_text


def test_validate_ocr_text_success():
    validate_ocr_text("Valid text content")
    validate_ocr_text("  Valid with spaces  ")


def test_validate_ocr_text_failure():
    with pytest.raises(ValueError):
        validate_ocr_text("")
    
    with pytest.raises(ValueError):
        validate_ocr_text("   ")
    
    with pytest.raises(ValueError):
        validate_ocr_text(None)
