from dataclasses import dataclass


@dataclass(frozen=True)
class AnonymizationConfig:
    enable_validation: bool = True
