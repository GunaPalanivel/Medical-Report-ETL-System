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

    def run_batch_parallel(self, pdf_paths: List[str], json_output_path: str, max_workers: int = None) -> List[PipelineContext]:
        """Run pipeline in parallel using ProcessPoolExecutor."""
        import concurrent.futures
        
        results: List[PipelineContext] = []
        metadata_list = []
        
        # Use helper function to avoid pickling bound methods if possible, 
        # but self.run_single should work if self is picklable.
        # If self contains unpicklable resources (like open files), this will fail.
        # Assuming stages are data-only configuration + code.

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, initializer=_worker_init) as executor:
            # We map run_single to pdf_paths
            future_to_pdf = {executor.submit(self.run_single, pdf_path): pdf_path for pdf_path in pdf_paths}
            
            for future in concurrent.futures.as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    context = future.result()
                    results.append(context)
                    if not context.has_errors():
                        metadata_list.append(context.metadata)
                except Exception as exc:
                    # Handle process crashes or serialization errors
                    error_context = PipelineContext(pdf_path=pdf_path)
                    error_context.add_error("System", f"Worker process failed: {str(exc)}")
                    results.append(error_context)

        if metadata_list:
            self._json_serializer.serialize(metadata_list, json_output_path)

        return results


def _worker_init():
    """Initialize worker process environment."""
    import os
    # Limit Tesseract/OpenMP threads to prevent CPU oversubscription
    os.environ["OMP_THREAD_LIMIT"] = "1"

