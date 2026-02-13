import re
from typing import List, Optional

from .base import BaseExtractor


class FindingsExtractor(BaseExtractor):
    @property
    def field_name(self) -> str:
        return "findings"

    def extract(self, text: str) -> Optional[List[str]]:
        match = re.search(
            r"Examination Findings\s*(.*?)\s*Conclusion",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if not match:
            return None
        findings_text = match.group(1)
        lines = [line.strip() for line in findings_text.strip().split("\n") if line.strip()]
        return lines or None

    def validate(self, value: object) -> bool:
        return isinstance(value, list)
