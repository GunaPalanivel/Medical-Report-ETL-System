from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataConfig:
    include_findings: bool = True
