import warnings

import pytest

from src import anonymizer, extractor, json_writer, pdf_handler


def test_anonymize_text_warns():
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        anonymized = anonymizer.anonymize_text("Patient Name: Jane Doe")

    assert anonymized
    assert any(item.category is DeprecationWarning for item in captured)


def test_extract_metadata_warns():
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        metadata = extractor.extract_metadata("Age: 30\nBMI: 25")

    assert metadata
    assert any(item.category is DeprecationWarning for item in captured)


def test_save_metadata_json_warns(tmp_path):
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        json_writer.save_metadata_json(
            [{"patient_id": "id-1", "age": 30, "BMI": 25, "findings": []}],
            str(tmp_path / "meta.json"),
        )

    assert (tmp_path / "meta.json").exists()
    assert any(item.category is DeprecationWarning for item in captured)


def test_pdf_handler_facades(monkeypatch, tmp_path):
    class _StubEngine:
        def extract_text(self, pdf_path):
            return "stub text"

    class _StubGenerator:
        def generate(self, anonymized_text, output_path):
            with open(output_path, "w", encoding="utf-8") as handle:
                handle.write(anonymized_text)

    monkeypatch.setattr(pdf_handler, "_ocr_engine", _StubEngine())
    monkeypatch.setattr(pdf_handler, "_pdf_generator", _StubGenerator())

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        text = pdf_handler.read_pdf_text("sample.pdf")
        pdf_handler.write_anonymized_pdf("sample.pdf", str(tmp_path / "out.pdf"), "safe")

    assert text == "stub text"
    assert (tmp_path / "out.pdf").exists()
    assert any(item.category is DeprecationWarning for item in captured)
