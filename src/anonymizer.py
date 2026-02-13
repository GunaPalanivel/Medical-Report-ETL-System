import warnings

from src.features.anonymization import PIIRedactor, build_default_registry


_registry = build_default_registry()
_redactor = PIIRedactor(_registry.get_all())


def anonymize_text(text):
    """Backward-compatible wrapper for PII redaction."""
    warnings.warn(
        "anonymize_text is deprecated; use PIIRedactor from src.features.anonymization",
        DeprecationWarning,
        stacklevel=2,
    )
    return _redactor.redact(text)
