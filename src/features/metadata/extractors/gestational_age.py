import re
from typing import Optional

from .base import BaseExtractor


class GestationalAgeExtractor(BaseExtractor):
    @property
    def field_name(self) -> str:
        return "gestational_age"

    def extract(self, text: str) -> Optional[str]:
        match = re.search(r"GA[:\-]?\s*(\d+\s*weeks?\s*\d*\s*day[s]?)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def validate(self, value: object) -> bool:
        return isinstance(value, str) and len(value) > 0
