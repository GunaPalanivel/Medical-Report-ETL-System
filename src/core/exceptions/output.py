from .base import ETLException


class OutputException(ETLException):
    """Output generation failed."""


class PDFGenerationException(OutputException):
    """Anonymized PDF generation failed."""


class JSONSerializationException(OutputException):
    """Metadata JSON serialization failed."""
