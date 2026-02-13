from src.pipeline import PipelineContext


def test_context_tracks_errors():
    context = PipelineContext(pdf_path="sample.pdf")
    assert context.has_errors() is False

    context.add_error("OCR", "failed")

    assert context.has_errors() is True
    assert context.errors == ["OCR: failed"]
