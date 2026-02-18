import json
import pytest

from src.core.exceptions import JSONSerializationException
from src.features.output import JSONSerializer, PDFGenerator


def test_json_serializer_outputs_aliases(tmp_path):
    output_path = tmp_path / "metadata.json"
    serializer = JSONSerializer()

    serializer.serialize(
        [
            {
                "patient_id": "test-id",
                "gestational_age": "40 weeks",
                "age": 30,
                "BMI": 28.5,
                "findings": ["Normal"],
            }
        ],
        str(output_path),
    )

    payload = output_path.read_text(encoding="utf-8")
    assert "demographic_age" in payload
    assert "examination_findings" in payload
    assert "findings" in payload


def test_pdf_generator_creates_file(tmp_path):
    output_path = tmp_path / "report.pdf"
    generator = PDFGenerator()

    generator.generate("Line 1\nLine 2", str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_json_serializer_empty_list(tmp_path):
    output_path = tmp_path / "empty.json"
    JSONSerializer().serialize([], str(output_path))

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data == {"dataResources": []}


def test_json_serializer_missing_optional_fields(tmp_path):
    output_path = tmp_path / "partial.json"
    JSONSerializer().serialize(
        [{"patient_id": "id-only"}],
        str(output_path),
    )

    data = json.loads(output_path.read_text(encoding="utf-8"))
    record = data["dataResources"][0]
    assert record["patient_id"] == "id-only"
    assert record["age"] is None
    assert record["findings"] == []


def test_json_serializer_invalid_path_raises():
    with pytest.raises(JSONSerializationException):
        JSONSerializer().serialize(
            [{"patient_id": "x"}],
            "/non/existent/dir/file.json",
        )


def test_pdf_generator_unicode_text(tmp_path):
    output_path = tmp_path / "unicode.pdf"
    PDFGenerator().generate("Héllo Wörld — résumé", str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_pdf_generator_empty_text(tmp_path):
    output_path = tmp_path / "empty.pdf"
    PDFGenerator().generate("", str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0
