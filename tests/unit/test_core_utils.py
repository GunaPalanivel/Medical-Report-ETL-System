import json
import pytest
from unittest.mock import Mock, patch
from src.core.utils.retry import retry_on_exception
from src.core.utils.file_utils import ensure_directory, get_pdf_files, atomic_write_json, write_lines
from src.core.utils.validation import validate_text_not_empty, validate_file_exists, validate_pdf


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


def test_atomic_write_json_creates_valid_json(tmp_path):
    output = tmp_path / "data.json"
    payload = {"key": "value", "nested": [1, 2, 3]}

    atomic_write_json(str(output), payload)

    assert output.exists()
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == payload


def test_atomic_write_json_replaces_existing(tmp_path):
    output = tmp_path / "data.json"
    output.write_text('{"old": true}', encoding="utf-8")

    atomic_write_json(str(output), {"new": True})

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == {"new": True}
    assert "old" not in loaded


def test_atomic_write_no_temp_file_left(tmp_path):
    output = tmp_path / "data.json"
    atomic_write_json(str(output), {"k": "v"})

    temp_file = tmp_path / "data.json.tmp"
    assert not temp_file.exists()


def test_write_lines_creates_file(tmp_path):
    output = tmp_path / "lines.txt"
    write_lines(str(output), ["line1", "line2", "line3"])

    content = output.read_text(encoding="utf-8")
    assert content == "line1\nline2\nline3\n"


def test_validate_file_exists_raises_for_missing():
    with pytest.raises(FileNotFoundError):
        validate_file_exists("/non/existent/file.pdf")


def test_validate_file_exists_passes(tmp_path):
    f = tmp_path / "exists.pdf"
    f.touch()
    validate_file_exists(str(f))  # should not raise


def test_validate_pdf_rejects_non_pdf():
    with pytest.raises(ValueError):
        validate_pdf("report.docx")
    with pytest.raises(ValueError):
        validate_pdf("image.png")


def test_validate_pdf_accepts_pdf():
    validate_pdf("report.pdf")
    validate_pdf("REPORT.PDF")
