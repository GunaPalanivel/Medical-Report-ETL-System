"""Pipeline stage contract tests — verifies precondition guards and data flow.

Each stage has a precondition (e.g., 'extracted_text must be set'). These tests
verify the guards AND the happy paths that set expected output fields.
Uses shared stubs from conftest.py to avoid duplication.
"""

import pytest
from tests.conftest import (
    StubOCREngine,
    StubRedactor,
    StubValidator,
    StubMetadataExtractor,
    StubUUIDService,
    StubPDFGenerator,
)
from src.pipeline import (
    AnonymizationStage,
    ExtractionStage,
    OCRStage,
    OutputStage,
    PipelineContext,
)


# ---------------------------------------------------------------------------
#  OCR Stage
# ---------------------------------------------------------------------------

def test_ocr_stage_happy_path():
    stage = OCRStage(StubOCREngine(text="extracted text"))
    ctx = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert ctx.extracted_text == "extracted text"
    assert not ctx.has_errors()


def test_ocr_stage_records_errors():
    stage = OCRStage(StubOCREngine(should_fail=True))
    ctx = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert ctx.has_errors()
    assert ctx.extracted_text is None


# ---------------------------------------------------------------------------
#  Anonymization Stage
# ---------------------------------------------------------------------------

def test_anonymization_stage_happy_path():
    stage = AnonymizationStage(StubRedactor(), StubValidator(valid=True))
    ctx = PipelineContext(pdf_path="file.pdf", extracted_text="raw text")

    ctx = stage.execute(ctx)

    assert ctx.anonymized_text == "raw text"
    assert not ctx.has_errors()


def test_anonymization_stage_requires_text():
    stage = AnonymizationStage(StubRedactor(), StubValidator())
    ctx = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert ctx.has_errors()


def test_anonymization_stage_validation_failure():
    stage = AnonymizationStage(StubRedactor(), StubValidator(valid=False))
    ctx = PipelineContext(pdf_path="file.pdf", extracted_text="raw")

    ctx = stage.execute(ctx)

    assert ctx.has_errors()


def test_anonymization_stage_exception_in_redactor():
    def blow_up(text):
        raise RuntimeError("redactor crash")

    stage = AnonymizationStage(StubRedactor(transform_fn=blow_up), StubValidator())
    ctx = PipelineContext(pdf_path="file.pdf", extracted_text="raw")
    ctx = stage.execute(ctx)

    assert ctx.has_errors()
    assert any("redactor crash" in e or "Anonymization" in e for e in ctx.errors)


# ---------------------------------------------------------------------------
#  Extraction Stage
# ---------------------------------------------------------------------------

def test_extraction_stage_happy_path():
    stage = ExtractionStage(StubMetadataExtractor({"age": 30, "BMI": 25.5}))
    ctx = PipelineContext(pdf_path="file.pdf", anonymized_text="clean text")

    ctx = stage.execute(ctx)

    assert ctx.metadata["age"] == 30
    assert ctx.metadata["BMI"] == 25.5
    assert not ctx.has_errors()


def test_extraction_stage_requires_text():
    stage = ExtractionStage(StubMetadataExtractor())
    ctx = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert ctx.has_errors()


def test_extraction_stage_exception_in_extractor():
    class _BrokenExtractor:
        def extract_all(self, text):
            raise RuntimeError("extractor crash")

    stage = ExtractionStage(_BrokenExtractor())
    ctx = PipelineContext(pdf_path="file.pdf", anonymized_text="text")
    ctx = stage.execute(ctx)

    assert ctx.has_errors()


# ---------------------------------------------------------------------------
#  Output Stage
# ---------------------------------------------------------------------------

def test_output_stage_happy_path(tmp_path):
    gen = StubPDFGenerator()
    uuid_svc = StubUUIDService()
    stage = OutputStage(gen, uuid_svc, str(tmp_path))

    ctx = PipelineContext(pdf_path="file.pdf", anonymized_text="clean text")
    ctx.metadata = {"patient_id": "PAT-001"}

    ctx = stage.execute(ctx)

    assert ctx.anonymized_pdf_path is not None
    assert not ctx.has_errors()
    assert len(gen.calls) == 1


def test_output_stage_requires_text(tmp_path):
    stage = OutputStage(StubPDFGenerator(), StubUUIDService(), str(tmp_path))
    ctx = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert ctx.has_errors()
