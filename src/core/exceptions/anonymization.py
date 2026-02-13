from .base import ETLException


class AnonymizationException(ETLException):
    """Anonymization-related errors."""


class RedactionException(AnonymizationException):
    """PII redaction failed."""


class UUIDMappingException(AnonymizationException):
    """UUID mapping persistence failed."""
