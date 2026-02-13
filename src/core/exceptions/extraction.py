from .base import ETLException


class ExtractionException(ETLException):
    """Metadata extraction failed."""


class FieldValidationException(ExtractionException):
    """Extracted field failed validation."""
