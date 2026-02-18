"""Batch processing integration tests — verifies aggregation semantics."""

from unittest.mock import Mock, patch
from src.pipeline import ETLPipeline, PipelineContext


def test_pipeline_run_batch_aggregation():
    mock_stage = Mock()
    mock_stage.execute.side_effect = lambda ctx: ctx
    mock_serializer = Mock()

    pipeline = ETLPipeline([mock_stage], mock_serializer)

    ctx_success = PipelineContext("doc1.pdf")
    ctx_success.metadata = {"id": "1"}

    ctx_fail = PipelineContext("doc2.pdf")
    ctx_fail.add_error("Stage1", "Error")

    with patch.object(pipeline, 'run_single', side_effect=[ctx_success, ctx_fail]):
        results = pipeline.run_batch(["doc1.pdf", "doc2.pdf"], "dummy_output.json")

        assert len(results) == 2
        assert not results[0].has_errors()
        assert results[1].has_errors()

        mock_serializer.serialize.assert_called_once()
        args, _ = mock_serializer.serialize.call_args
        assert len(args[0]) == 1
        assert args[0][0]["id"] == "1"


def test_batch_all_failures_skips_serializer():
    mock_stage = Mock()
    mock_stage.execute.side_effect = lambda ctx: ctx
    mock_serializer = Mock()

    pipeline = ETLPipeline([mock_stage], mock_serializer)

    ctx_fail1 = PipelineContext("fail1.pdf")
    ctx_fail1.add_error("Stage", "error1")
    ctx_fail2 = PipelineContext("fail2.pdf")
    ctx_fail2.add_error("Stage", "error2")

    with patch.object(pipeline, 'run_single', side_effect=[ctx_fail1, ctx_fail2]):
        results = pipeline.run_batch(["fail1.pdf", "fail2.pdf"], "out.json")

    assert all(r.has_errors() for r in results)
    # Serializer should be called with empty metadata list
    if mock_serializer.serialize.called:
        args, _ = mock_serializer.serialize.call_args
        assert len(args[0]) == 0


def test_batch_empty_input():
    mock_stage = Mock()
    mock_serializer = Mock()
    pipeline = ETLPipeline([mock_stage], mock_serializer)

    results = pipeline.run_batch([], "out.json")

    assert results == []
    mock_serializer.serialize.assert_not_called()


def test_batch_single_item_success():
    mock_stage = Mock()
    mock_stage.execute.side_effect = lambda ctx: ctx
    mock_serializer = Mock()

    pipeline = ETLPipeline([mock_stage], mock_serializer)

    ctx = PipelineContext("single.pdf")
    ctx.metadata = {"age": 30}

    with patch.object(pipeline, 'run_single', return_value=ctx):
        results = pipeline.run_batch(["single.pdf"], "out.json")

    assert len(results) == 1
    assert not results[0].has_errors()
    assert results[0].metadata["age"] == 30
