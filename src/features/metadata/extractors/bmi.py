import re
from typing import Optional

from .base import BaseExtractor


class BMIExtractor(BaseExtractor):
    @property
    def field_name(self) -> str:
        return "BMI"

    def extract(self, text: str) -> Optional[float]:
        match = re.search(r"BMI[:\-]?\s*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def validate(self, value: object) -> bool:
        return isinstance(value, float) and 0.0 <= value <= 100.0
