from src.pipeline import (
    AnonymizationStage,
    ExtractionStage,
    OCRStage,
    OutputStage,
    PipelineContext,
)


class _StubOCREngine:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def extract_text(self, pdf_path):
        if self.should_fail:
            raise RuntimeError("OCR failed")
        return "raw text"


class _StubRedactor:
    def redact(self, text):
        return text


class _StubValidator:
    def __init__(self, valid=True):
        self.valid = valid

    def validate(self, text):
        return self.valid


class _StubExtractor:
    def extract_all(self, text):
        return {"age": 30}


class _StubUUIDService:
    def get_or_create_uuid(self, original_id):
        return "uuid-123"


class _StubPDFGenerator:
    def generate(self, anonymized_text, output_path):
        return None


def test_ocr_stage_records_errors():
    stage = OCRStage(_StubOCREngine(should_fail=True))
    context = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert context.has_errors() is True


def test_anonymization_stage_requires_text():
    stage = AnonymizationStage(_StubRedactor(), _StubValidator())
    context = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert context.has_errors() is True


def test_anonymization_stage_validation_failure():
    stage = AnonymizationStage(_StubRedactor(), _StubValidator(valid=False))
    context = PipelineContext(pdf_path="file.pdf", extracted_text="raw")

    context = stage.execute(context)

    assert context.has_errors() is True


def test_extraction_stage_requires_text():
    stage = ExtractionStage(_StubExtractor())
    context = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert context.has_errors() is True


def test_output_stage_requires_text(tmp_path):
    stage = OutputStage(_StubPDFGenerator(), _StubUUIDService(), str(tmp_path))
    context = stage.execute(PipelineContext(pdf_path="file.pdf"))

    assert context.has_errors() is True
