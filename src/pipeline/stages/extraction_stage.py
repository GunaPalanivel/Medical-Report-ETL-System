from src.features.metadata import MetadataExtractor

from ..context import PipelineContext
from .base import BasePipelineStage


class ExtractionStage(BasePipelineStage):
    name = "Extraction"

    def __init__(self, extractor: MetadataExtractor) -> None:
        self._extractor = extractor

    def execute(self, context: PipelineContext) -> PipelineContext:
        if context.anonymized_text is None:
            context.add_error(self.name, "No anonymized text")
            return context
        try:
            context.metadata = self._extractor.extract_all(context.anonymized_text)
        except Exception as exc:
            context.add_error(self.name, str(exc))
        return context
