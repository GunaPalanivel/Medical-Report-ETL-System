import os

import pytest

from main import build_pipeline
from src.core import Settings, get_pdf_files
from src.features.output import JSONSerializer


def _integration_enabled() -> bool:
    return os.getenv("RUN_INTEGRATION_TESTS") == "1"


@pytest.mark.skipif(not _integration_enabled(), reason="Set RUN_INTEGRATION_TESTS=1 to run")
def test_pipeline_runs_on_sample_pdf():
    settings = Settings.load()
    pdf_files = get_pdf_files(settings.input_dir)
    if not pdf_files:
        pytest.skip("No PDF files found in input directory")

    pipeline = build_pipeline(settings)
    results = pipeline.run_batch([pdf_files[0]], settings.json_output)

    assert len(results) == 1
    assert not results[0].has_errors()


def test_json_serializer_aliases(tmp_path):
    serializer = JSONSerializer()
    output_path = tmp_path / "metadata.json"

    metadata = {
        "patient_id": "test-id",
        "gestational_age": "40 weeks",
        "age": 30,
        "BMI": 28.5,
        "findings": ["Normal"],
    }

    serializer.serialize([metadata], str(output_path))

    payload = output_path.read_text(encoding="utf-8")
    assert "demographic_age" in payload
    assert "examination_findings" in payload
    assert "age" in payload
    assert "findings" in payload
