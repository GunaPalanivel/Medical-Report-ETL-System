from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PipelineContext:
    pdf_path: str
    extracted_text: Optional[str] = None
    anonymized_text: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)
    anonymized_pdf_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    def add_error(self, stage: str, message: str) -> None:
        self.errors.append(f"{stage}: {message}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0
