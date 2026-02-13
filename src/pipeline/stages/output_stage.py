import os
from pathlib import Path

from src.features.anonymization import UUIDMappingService
from src.features.output import PDFGenerator

from ..context import PipelineContext
from .base import BasePipelineStage


class OutputStage(BasePipelineStage):
    name = "Output"

    def __init__(self, pdf_generator: PDFGenerator, uuid_service: UUIDMappingService, output_dir: str) -> None:
        self._pdf_generator = pdf_generator
        self._uuid_service = uuid_service
        self._output_dir = output_dir

    def execute(self, context: PipelineContext) -> PipelineContext:
        if context.anonymized_text is None:
            context.add_error(self.name, "No anonymized text")
            return context

        try:
            real_id = Path(context.pdf_path).stem
            anon_id = self._uuid_service.get_or_create_uuid(real_id)
            context.metadata["patient_id"] = anon_id

            os.makedirs(self._output_dir, exist_ok=True)
            output_path = os.path.join(self._output_dir, f"{anon_id}.pdf")
            self._pdf_generator.generate(context.anonymized_text, output_path)
            context.anonymized_pdf_path = output_path
        except Exception as exc:
            context.add_error(self.name, str(exc))

        return context
