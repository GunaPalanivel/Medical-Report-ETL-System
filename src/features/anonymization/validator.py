import re
from typing import Iterable

from .pii_patterns import PIIPattern


class RedactionValidator:
    """Validate that text no longer contains PII patterns."""

    def __init__(self, patterns: Iterable[PIIPattern]) -> None:
        self._patterns = list(patterns)

    def validate(self, text: str) -> bool:
        for pattern in self._patterns:
            if re.search(pattern.regex, text):
                return False
        return True
