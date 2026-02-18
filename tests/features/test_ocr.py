import pytest

from src.core.exceptions import OCRException
from src.features.ocr import OCRConfig, OCREngine


class _StubConverter:
    def __init__(self, images):
        self._images = images
        self.last_dpi = None

    def convert(self, pdf_path, dpi):
        self.last_dpi = dpi
        return self._images


class _StubExtractor:
    def __init__(self, outputs):
        self._outputs = outputs
        self.calls = []

    def extract(self, image):
        self.calls.append(image)
        return self._outputs.pop(0)


def test_ocr_engine_extracts_text(monkeypatch):
    converter = _StubConverter(["img1", "img2"])
    extractor = _StubExtractor(["page1", "page2"])

    class _FakeConverter:
        def __init__(self, poppler_path):
            self.poppler_path = poppler_path

        def convert(self, pdf_path, dpi):
            return converter.convert(pdf_path, dpi)

    class _FakeExtractor:
        def __init__(self, tesseract_path, language):
            self.tesseract_path = tesseract_path
            self.language = language

        def extract(self, image):
            return extractor.extract(image)

    monkeypatch.setattr("src.features.ocr.engine.PDFConverter", _FakeConverter)
    monkeypatch.setattr("src.features.ocr.engine.TextExtractor", _FakeExtractor)

    config = OCRConfig(
        tesseract_path="/tmp/tesseract",
        poppler_path="/tmp/poppler",
        dpi=300,
        language="eng",
    )
    engine = OCREngine(config)

    text = engine.extract_text("report.pdf")

    assert text == "page1\npage2"
    assert converter.last_dpi == 300
    assert extractor.calls == ["img1", "img2"]


def test_ocr_engine_raises_on_empty_text(monkeypatch):
    converter = _StubConverter(["img1"])
    extractor = _StubExtractor([""])

    class _FakeConverter:
        def __init__(self, poppler_path):
            self.poppler_path = poppler_path

        def convert(self, pdf_path, dpi):
            return converter.convert(pdf_path, dpi)

    class _FakeExtractor:
        def __init__(self, tesseract_path, language):
            self.tesseract_path = tesseract_path
            self.language = language

        def extract(self, image):
            return extractor.extract(image)

    monkeypatch.setattr("src.features.ocr.engine.PDFConverter", _FakeConverter)
    monkeypatch.setattr("src.features.ocr.engine.TextExtractor", _FakeExtractor)

    config = OCRConfig(
        tesseract_path="/tmp/tesseract",
        poppler_path="/tmp/poppler",
        dpi=300,
        language="eng",
    )
    engine = OCREngine(config)

    with pytest.raises(OCRException):
        engine.extract_text("report.pdf")
