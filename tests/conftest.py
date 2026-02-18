import os
import sys
import pickle
import pytest
from pathlib import Path
from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PYTHONPATH", str(ROOT))


# ---------------------------------------------------------------------------
#  Shared Stubs — single source of truth for all test layers
# ---------------------------------------------------------------------------

class StubOCREngine:
    """Configurable OCR engine stub."""
    def __init__(self, text="raw text", should_fail=False):
        self._text = text
        self._should_fail = should_fail

    def extract_text(self, pdf_path):
        if self._should_fail:
            raise RuntimeError("OCR failed")
        return self._text


class StubRedactor:
    """Redactor with injectable transform function."""
    def __init__(self, transform_fn=None):
        self._fn = transform_fn or (lambda t: t)

    def redact(self, text):
        return self._fn(text)


class StubValidator:
    """Configurable validation result."""
    def __init__(self, valid=True):
        self._valid = valid

    def validate(self, text):
        return self._valid


class StubMetadataExtractor:
    """Returns fixed metadata dict."""
    def __init__(self, metadata=None):
        self._metadata = metadata or {"age": 30}

    def extract_all(self, text):
        return dict(self._metadata)


class StubUUIDService:
    """Deterministic UUID mapping."""
    def __init__(self, mapping=None):
        self._mapping = mapping or {}
        self._counter = 0

    def get_or_create_uuid(self, original_id):
        if original_id in self._mapping:
            return self._mapping[original_id]
        self._counter += 1
        uid = f"uuid-{self._counter:03d}"
        self._mapping[original_id] = uid
        return uid


class StubPDFGenerator:
    """PDF generation stub that optionally writes a marker file."""
    def __init__(self, should_fail=False):
        self._should_fail = should_fail
        self.calls = []

    def generate(self, anonymized_text, output_path):
        self.calls.append((anonymized_text, output_path))
        if self._should_fail:
            raise RuntimeError("PDF generation failed")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text("stub-pdf", encoding="utf-8")


class StubSerializer:
    """Captures serialize calls for assertions."""
    def __init__(self):
        self.calls = []

    def serialize(self, metadata_list, output_path):
        self.calls.append((list(metadata_list), output_path))


# ---------------------------------------------------------------------------
#  Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def generate_test_pdf(tmp_path):
    """Fixture to generate a temporary PDF file with specified text."""
    def _create_pdf(content: str, filename: str = "test.pdf") -> str:
        pdf_path = tmp_path / filename
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in content.split('\n'):
            pdf.cell(200, 10, txt=line, ln=1, align='L')
        pdf.output(str(pdf_path))
        return str(pdf_path)
    return _create_pdf


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture to ensure a temporary output directory exists."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)


@pytest.fixture
def sample_medical_text():
    """Realistic medical report text containing all extractable fields."""
    return (
        "Patient Name: Jane Doe\n"
        "Patient ID: PAT-12345\n"
        "Hospital Name: City General Hospital\n"
        "Clinician: Dr. Smith\n"
        "Age: 33\n"
        "BMI: 28.5\n"
        "GA: 24 weeks 3 days\n"
        "Examination Findings\n"
        "Head : Normal skull appearance\n"
        "Brain : No choroid plexus cyst seen\n"
        "Conclusion\n"
        "Normal scan\n"
    )
