import warnings

from src.core import Settings
from src.features.ocr import OCREngine, load_ocr_config
from src.features.output import PDFGenerator


_settings = Settings.load()
_ocr_engine = OCREngine(load_ocr_config(_settings))
_pdf_generator = PDFGenerator()


def write_anonymized_pdf(original_path, output_path, anonymized_text):
    """Backward-compatible wrapper for PDF generation."""
    warnings.warn(
        "write_anonymized_pdf is deprecated; use PDFGenerator from src.features.output",
        DeprecationWarning,
        stacklevel=2,
    )
    _pdf_generator.generate(anonymized_text, output_path)


def read_pdf_text(pdf_path):
    """Backward-compatible wrapper for OCR text extraction."""
    warnings.warn(
        "read_pdf_text is deprecated; use OCREngine from src.features.ocr",
        DeprecationWarning,
        stacklevel=2,
    )
    return _ocr_engine.extract_text(pdf_path)

