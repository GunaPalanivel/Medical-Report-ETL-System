from typing import Iterable, List

from src.features.output import JSONSerializer

from .context import PipelineContext
from .stages.base import BasePipelineStage


class ETLPipeline:
    def __init__(self, stages: Iterable[BasePipelineStage], json_serializer: JSONSerializer) -> None:
        self._stages = list(stages)
        self._json_serializer = json_serializer

    def run_single(self, pdf_path: str) -> PipelineContext:
        context = PipelineContext(pdf_path=pdf_path)
        for stage in self._stages:
            context = stage.execute(context)
        return context

    def run_batch(self, pdf_paths: List[str], json_output_path: str) -> List[PipelineContext]:
        results: List[PipelineContext] = []
        metadata_list = []

        for pdf_path in pdf_paths:
            context = self.run_single(pdf_path)
            results.append(context)
            if not context.has_errors():
                metadata_list.append(context.metadata)

        if metadata_list:
            self._json_serializer.serialize(metadata_list, json_output_path)

        return results
