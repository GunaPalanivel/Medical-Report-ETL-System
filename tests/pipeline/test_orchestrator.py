from src.pipeline import ETLPipeline, PipelineContext


class _StubStage:
    def __init__(self, metadata=None):
        self._metadata = metadata or {}

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.metadata.update(self._metadata)
        return context


class _StubSerializer:
    def __init__(self):
        self.called_with = None

    def serialize(self, metadata_list, output_path):
        self.called_with = (metadata_list, output_path)


def test_pipeline_runs_batch_and_serializes(tmp_path):
    serializer = _StubSerializer()
    pipeline = ETLPipeline([_StubStage({"age": 30})], serializer)

    results = pipeline.run_batch(["a.pdf"], str(tmp_path / "out.json"))

    assert len(results) == 1
    assert results[0].metadata["age"] == 30
    assert serializer.called_with is not None
