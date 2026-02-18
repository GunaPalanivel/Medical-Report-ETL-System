import pytest
import dataclasses
from pathlib import Path
from src.core import Settings
import sys
from unittest.mock import patch

# Add project root to sys.path to import main
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from main import build_pipeline

def test_parallel_correctness(generate_test_pdf, tmp_path):
    """
    Verify parallel execution produces identical results to sequential execution
    using synthetic PDF data.
    """
    # 1. Setup - Create synthetic data
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    pdf_files = []
    for i in range(5):
        content = f"Patient Name: John Doe {i}\nPatient ID: 12345{i}\nClinical Findings: Normal."
        pdf_path = generate_test_pdf(content, filename=f"test_patient_{i}.pdf")
        # Move to input_dir to mimic real setup, though generate_test_pdf puts in tmp_path
        # Actually generate_test_pdf uses tmp_path, we can just use those paths.
        pdf_files.append(pdf_path)

    # 2. Configure Settings
    # Load default settings from env or defaults
    base_settings = Settings.load()
    
    # Override paths to use our temp directories
    settings = dataclasses.replace(
        base_settings,
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        json_output=str(output_dir / "metadata.json"),
        id_map_file=str(output_dir / "id_map.json")
    )

    # Mock OCREngine to avoid slow/unstable OCR
    with patch("src.features.ocr.OCREngine.extract_text", return_value="Patient Name: John Doe\nPatient ID: 12345\nExpected content"):
        # Mock ProcessPoolExecutor to use ThreadPoolExecutor to allow mocks to work and speed up test
        import concurrent.futures
        with patch('concurrent.futures.ProcessPoolExecutor', side_effect=concurrent.futures.ThreadPoolExecutor):
            # 3. Build Pipeline
            pipeline = build_pipeline(settings)

            # 4. Run Sequential
            seq_output_json = output_dir / "seq_metadata.json"
            seq_results = pipeline.run_batch(pdf_files, str(seq_output_json))
            
            # 5. Run Parallel
            par_output_json = output_dir / "par_metadata.json"
            # Use 2 workers to ensure parallelism
            par_results = pipeline.run_batch_parallel(pdf_files, str(par_output_json), max_workers=2)

            # 6. Compare Results
            # Sort by pdf_path to handle out-of-order completion
            seq_results.sort(key=lambda x: x.pdf_path)
            par_results.sort(key=lambda x: x.pdf_path)

            assert len(seq_results) == len(par_results)
            
            for seq, par in zip(seq_results, par_results):
                assert seq.pdf_path == par.pdf_path
                assert seq.has_errors() == par.has_errors()
                
                if not seq.has_errors():
                    # Compare metadata
                    # Note: We might want to remove 'processing_time' or similar non-deterministic fields if they exist
                    # But straightforward strict equality is good for start
                    assert seq.metadata == par.metadata

    print("\nParallel execution correctness verified with synthetic data (Mocked OCR, ThreadPool)!")
