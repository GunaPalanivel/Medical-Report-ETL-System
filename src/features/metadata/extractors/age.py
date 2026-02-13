import re
from typing import Optional

from .base import BaseExtractor


class AgeExtractor(BaseExtractor):
    @property
    def field_name(self) -> str:
        return "age"

    def extract(self, text: str) -> Optional[int]:
        match = re.search(r"Age[:\-]?\s*(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def validate(self, value: object) -> bool:
        return isinstance(value, int) and 0 <= value <= 120
