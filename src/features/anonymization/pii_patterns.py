from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PIIPattern:
    name: str
    regex: str
    replacement: str
    priority: int = 0


class PIIPatternRegistry:
    def __init__(self) -> None:
        self._patterns: Dict[str, PIIPattern] = {}

    def register(self, pattern: PIIPattern) -> None:
        self._patterns[pattern.name] = pattern

    def get_all(self) -> List[PIIPattern]:
        return sorted(self._patterns.values(), key=lambda p: p.priority)


def build_default_registry() -> PIIPatternRegistry:
    registry = PIIPatternRegistry()
    registry.register(
        PIIPattern(
            name="patient_name",
            regex=r"Patient Name[:\s]+[A-Za-z][A-Za-z \t]+",
            replacement="Patient Name: [ANONYMIZED]",
            priority=10,
        )
    )
    registry.register(
        PIIPattern(
            name="patient_id",
            regex=r"Patient ID[:\s]+[A-Za-z0-9][A-Za-z0-9_-]*",
            replacement="Patient ID: [ANONYMIZED]",
            priority=20,
        )
    )
    registry.register(
        PIIPattern(
            name="hospital_name",
            regex=r"Hospital Name[:\s]+[A-Za-z][A-Za-z \t]+",
            replacement="Hospital Name: [ANONYMIZED]",
            priority=30,
        )
    )
    registry.register(
        PIIPattern(
            name="clinician",
            regex=r"Clinician[:\s]+[A-Za-z][A-Za-z \t]+",
            replacement="Clinician: [ANONYMIZED]",
            priority=40,
        )
    )
    return registry
