"""Orchestrator tests — verifies pipeline wiring, batch semantics, and serializer calls.

Uses shared stubs from conftest.py.
"""

from tests.conftest import StubSerializer
from src.pipeline import ETLPipeline, PipelineContext


class _PassthroughStage:
    """Stub stage that sets metadata and passes through."""
    def __init__(self, metadata=None):
        self._metadata = metadata or {}

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.metadata.update(self._metadata)
        return context


class _ErrorStage:
    """Stub stage that always adds an error."""
    def execute(self, context: PipelineContext) -> PipelineContext:
        context.add_error("ErrorStage", "deliberate failure")
        return context


# ---------------------------------------------------------------------------
#  run_single
# ---------------------------------------------------------------------------

def test_run_single_returns_context():
    serializer = StubSerializer()
    pipeline = ETLPipeline([_PassthroughStage({"age": 30})], serializer)

    ctx = pipeline.run_single("a.pdf")

    assert isinstance(ctx, PipelineContext)
    assert ctx.pdf_path == "a.pdf"
    assert ctx.metadata["age"] == 30


# ---------------------------------------------------------------------------
#  run_batch
# ---------------------------------------------------------------------------

def test_pipeline_runs_batch_and_serializes(tmp_path):
    serializer = StubSerializer()
    pipeline = ETLPipeline([_PassthroughStage({"age": 30})], serializer)

    results = pipeline.run_batch(["a.pdf"], str(tmp_path / "out.json"))

    assert len(results) == 1
    assert results[0].metadata["age"] == 30
    assert len(serializer.calls) == 1


def test_run_batch_empty_list(tmp_path):
    serializer = StubSerializer()
    pipeline = ETLPipeline([_PassthroughStage()], serializer)

    results = pipeline.run_batch([], str(tmp_path / "out.json"))

    assert results == []
    assert len(serializer.calls) == 0


def test_run_batch_all_failures_skips_serialization(tmp_path):
    serializer = StubSerializer()
    pipeline = ETLPipeline([_ErrorStage()], serializer)

    results = pipeline.run_batch(["a.pdf", "b.pdf"], str(tmp_path / "out.json"))

    assert len(results) == 2
    assert all(r.has_errors() for r in results)
    # Serializer should still be called, but with empty metadata list
    if serializer.calls:
        metadata_list = serializer.calls[0][0]
        assert len(metadata_list) == 0


def test_run_batch_stages_execute_in_order(tmp_path):
    """Context flows through stages in the declared order."""
    order = []

    class _OrderTracker:
        def __init__(self, tag):
            self._tag = tag

        def execute(self, ctx):
            order.append(self._tag)
            return ctx

    serializer = StubSerializer()
    pipeline = ETLPipeline([_OrderTracker("A"), _OrderTracker("B"), _OrderTracker("C")], serializer)

    pipeline.run_batch(["test.pdf"], str(tmp_path / "out.json"))

    assert order == ["A", "B", "C"]


def test_serializer_receives_correct_output_path(tmp_path):
    serializer = StubSerializer()
    pipeline = ETLPipeline([_PassthroughStage()], serializer)
    out = str(tmp_path / "specific_output.json")

    pipeline.run_batch(["x.pdf"], out)

    assert serializer.calls[0][1] == out
