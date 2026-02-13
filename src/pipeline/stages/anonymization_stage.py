from src.features.anonymization import PIIRedactor, RedactionValidator

from ..context import PipelineContext
from .base import BasePipelineStage


class AnonymizationStage(BasePipelineStage):
    name = "Anonymization"

    def __init__(self, redactor: PIIRedactor, validator: RedactionValidator) -> None:
        self._redactor = redactor
        self._validator = validator

    def execute(self, context: PipelineContext) -> PipelineContext:
        if context.extracted_text is None:
            context.add_error(self.name, "No extracted text")
            return context
        try:
            context.anonymized_text = self._redactor.redact(context.extracted_text)
            if not self._validator.validate(context.anonymized_text):
                context.add_error(self.name, "Redaction validation failed")
        except Exception as exc:
            context.add_error(self.name, str(exc))
        return context
