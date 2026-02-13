import re
from typing import Iterable

from src.core.exceptions import RedactionException

from .pii_patterns import PIIPattern


class PIIRedactor:
    """Apply a registry of PII patterns to redact text."""

    def __init__(self, patterns: Iterable[PIIPattern]) -> None:
        self._patterns = list(patterns)

    def redact(self, text: str) -> str:
        try:
            redacted = text
            for pattern in self._patterns:
                redacted = re.sub(pattern.regex, pattern.replacement, redacted)
            return redacted
        except Exception as exc:
            raise RedactionException(str(exc)) from exc
