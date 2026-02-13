from unittest.mock import Mock, patch
from src.pipeline import ETLPipeline, PipelineContext


def test_pipeline_run_batch_aggregation():
    # Mock stages
    mock_stage = Mock()
    mock_stage.execute.side_effect = lambda ctx: ctx  # Pass-through
    
    # Mock serializer
    mock_serializer = Mock()
    
    pipeline = ETLPipeline([mock_stage], mock_serializer)
    
    # Mock run_single to return controlled contexts
    ctx_success = PipelineContext("doc1.pdf")
    ctx_success.metadata = {"id": "1"}
    
    ctx_fail = PipelineContext("doc2.pdf")
    ctx_fail.add_error("Stage1", "Error")
    
    with patch.object(pipeline, 'run_single', side_effect=[ctx_success, ctx_fail]):
        results = pipeline.run_batch(["doc1.pdf", "doc2.pdf"], "dummy_output.json")
        
        assert len(results) == 2
        assert not results[0].has_errors()
        assert results[1].has_errors()
        
        # Verify serializer called only with success metadata
        mock_serializer.serialize.assert_called_once()
        args, _ = mock_serializer.serialize.call_args
        assert len(args[0]) == 1
        assert args[0][0]["id"] == "1"
