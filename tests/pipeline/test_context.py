"""PipelineContext contract tests — verifies shared data contract between stages.

If context defaults or error format changes, stages break silently.
"""

import pickle
from src.pipeline import PipelineContext


def test_context_default_values():
    ctx = PipelineContext(pdf_path="sample.pdf")

    assert ctx.pdf_path == "sample.pdf"
    assert ctx.extracted_text is None
    assert ctx.anonymized_text is None
    assert ctx.anonymized_pdf_path is None
    assert ctx.errors == []


def test_context_metadata_is_dict():
    ctx = PipelineContext(pdf_path="x.pdf")
    assert isinstance(ctx.metadata, dict)
    assert ctx.metadata == {}


def test_context_tracks_errors():
    ctx = PipelineContext(pdf_path="sample.pdf")
    assert ctx.has_errors() is False

    ctx.add_error("OCR", "failed")

    assert ctx.has_errors() is True
    assert ctx.errors == ["OCR: failed"]


def test_context_multiple_errors_accumulate():
    ctx = PipelineContext(pdf_path="x.pdf")
    ctx.add_error("OCR", "timeout")
    ctx.add_error("Anonymization", "pattern fail")
    ctx.add_error("Extraction", "missing field")

    assert len(ctx.errors) == 3
    assert ctx.errors[0] == "OCR: timeout"
    assert ctx.errors[1] == "Anonymization: pattern fail"
    assert ctx.errors[2] == "Extraction: missing field"


def test_context_error_format():
    ctx = PipelineContext(pdf_path="x.pdf")
    ctx.add_error("StageName", "detail message")
    assert ctx.errors[0] == "StageName: detail message"


def test_context_is_picklable():
    """ProcessPoolExecutor serializes PipelineContext — must survive pickle round-trip."""
    ctx = PipelineContext(pdf_path="test.pdf")
    ctx.extracted_text = "raw"
    ctx.anonymized_text = "clean"
    ctx.metadata = {"age": 30, "BMI": 25.5}
    ctx.add_error("Test", "msg")

    restored = pickle.loads(pickle.dumps(ctx))

    assert restored.pdf_path == ctx.pdf_path
    assert restored.extracted_text == ctx.extracted_text
    assert restored.anonymized_text == ctx.anonymized_text
    assert restored.metadata == ctx.metadata
    assert restored.errors == ctx.errors
