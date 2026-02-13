from src.features.ocr import OCREngine

from ..context import PipelineContext
from .base import BasePipelineStage


class OCRStage(BasePipelineStage):
    name = "OCR"

    def __init__(self, engine: OCREngine) -> None:
        self._engine = engine

    def execute(self, context: PipelineContext) -> PipelineContext:
        try:
            context.extracted_text = self._engine.extract_text(context.pdf_path)
        except Exception as exc:
            context.add_error(self.name, str(exc))
        return context
