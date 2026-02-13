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
