import pytest
from unittest.mock import Mock, patch
from src.core.utils.retry import retry_on_exception
from src.core.utils.file_utils import ensure_directory, get_pdf_files
from src.core.utils.validation import validate_text_not_empty, validate_file_exists


def test_retry_success():
    mock_func = Mock(return_value="success")
    decorated = retry_on_exception(max_attempts=3)(mock_func)
    assert decorated() == "success"
    assert mock_func.call_count == 1


def test_retry_failure_then_success():
    mock_func = Mock(side_effect=[ValueError("Fail"), "Success"])
    decorated = retry_on_exception(max_attempts=3)(mock_func)
    
    # Mock time.sleep to speed up test
    with patch("time.sleep"):
        result = decorated()
    
    assert result == "Success"
    assert mock_func.call_count == 2


def test_retry_max_attempts_exceeded():
    mock_func = Mock(side_effect=ValueError("Fail"))
    decorated = retry_on_exception(max_attempts=2)(mock_func)
    
    with patch("time.sleep"):
        with pytest.raises(ValueError):
            decorated()
    
    assert mock_func.call_count == 2


def test_ensure_directory(tmp_path):
    target = tmp_path / "subdir" / "nested"
    ensure_directory(str(target))
    assert target.exists()
    assert target.is_dir()


def test_validate_text_not_empty():
    validate_text_not_empty("valid")
    with pytest.raises(ValueError):
        validate_text_not_empty("")
    with pytest.raises(ValueError):
        validate_text_not_empty("   ")


def test_get_pdf_files(tmp_path):
    (tmp_path / "a.pdf").touch()
    (tmp_path / "b.PDF").touch()
    (tmp_path / "c.txt").touch()
    
    pdfs = get_pdf_files(str(tmp_path))
    assert len(pdfs) == 2
    assert any("a.pdf" in p for p in pdfs)
    assert any("b.PDF" in p for p in pdfs)
