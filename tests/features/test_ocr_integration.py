import os
import pytest
from src.core import Settings
from src.features.ocr import OCREngine, load_ocr_config


@pytest.mark.integration
def test_ocr_engine_integration():
    settings = Settings.load()
    if not os.path.exists(settings.input_dir):
        pytest.skip("Input directory not found")
    
    pdf_files = [f for f in os.listdir(settings.input_dir) if f.endswith(".pdf")]
    if not pdf_files:
        pytest.skip("No PDF files found for integration test")
    
    target_pdf = os.path.join(settings.input_dir, pdf_files[0])
    
    config = load_ocr_config(settings)
    engine = OCREngine(config)
    
    text = engine.extract_text(target_pdf)
    assert text is not None
    assert len(text) > 0
    assert isinstance(text, str)
