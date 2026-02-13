from .base import ETLException


class OCRException(ETLException):
    """OCR-related errors."""


class PDFConversionException(OCRException):
    """PDF to image conversion failed."""


class TextExtractionException(OCRException):
    """OCR text extraction failed."""
