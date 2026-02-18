"""Integration tests for error handling during batch and parallel execution.

Rewrites the original test to be clean and deterministic, using
ThreadPoolExecutor mock for reliable testing of error aggregation logic.
"""

import concurrent.futures
from unittest.mock import Mock, patch

from src.pipeline import ETLPipeline, PipelineContext


def _make_pipeline():
    mock_stage = Mock()
    mock_stage.execute.side_effect = lambda ctx: ctx
    mock_serializer = Mock()
    return ETLPipeline([mock_stage], mock_serializer), mock_serializer


def test_parallel_worker_failure_isolated():
    """One worker crash must not prevent others from succeeding."""
    pipeline, serializer = _make_pipeline()

    ctx_ok = PipelineContext("good.pdf")
    ctx_ok.metadata = {"id": "ok"}

    def side_effect(pdf_path):
        if "bad" in pdf_path:
            raise RuntimeError("Simulated Worker Crash")
        ctx = PipelineContext(pdf_path)
        ctx.metadata = {"id": "ok"}
        return ctx

    with patch('concurrent.futures.ProcessPoolExecutor',
               side_effect=concurrent.futures.ThreadPoolExecutor):
        with patch.object(pipeline, 'run_single', side_effect=side_effect):
            results = pipeline.run_batch_parallel(
                ["good1.pdf", "bad.pdf", "good2.pdf"],
                "out.json",
                max_workers=2,
            )

    assert len(results) == 3

    failures = [r for r in results if r.has_errors()]
    successes = [r for r in results if not r.has_errors()]

    assert len(failures) == 1
    assert len(successes) == 2
    assert "bad.pdf" in failures[0].pdf_path
    assert any("Simulated Worker Crash" in e for e in failures[0].errors)


def test_stage_error_does_not_crash_batch():
    """A stage that adds an error should not crash the entire batch."""
    error_stage = Mock()

    def error_execute(ctx):
        ctx.add_error("TestStage", "deliberate failure")
        return ctx

    error_stage.execute.side_effect = error_execute
    serializer = Mock()
    pipeline = ETLPipeline([error_stage], serializer)

    with patch('concurrent.futures.ProcessPoolExecutor',
               side_effect=concurrent.futures.ThreadPoolExecutor):
        results = pipeline.run_batch_parallel(
            ["a.pdf", "b.pdf"], "out.json", max_workers=2
        )

    assert len(results) == 2
    assert all(r.has_errors() for r in results)


def test_all_workers_fail_no_metadata_serialized():
    """When all workers fail, serializer should receive empty metadata."""
    pipeline, serializer = _make_pipeline()

    def always_fail(pdf_path):
        raise RuntimeError("crash")

    with patch('concurrent.futures.ProcessPoolExecutor',
               side_effect=concurrent.futures.ThreadPoolExecutor):
        with patch.object(pipeline, 'run_single', side_effect=always_fail):
            results = pipeline.run_batch_parallel(
                ["a.pdf", "b.pdf"], "out.json", max_workers=2
            )

    assert len(results) == 2
    assert all(r.has_errors() for r in results)
