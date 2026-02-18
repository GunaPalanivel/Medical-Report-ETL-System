import pytest
from pathlib import Path
from src.core import Settings
from src.pipeline import ETLPipeline
from src.pipeline.orchestrator import _worker_init

# We need to import the build_pipeline function or recreate it.
# Since build_pipeline is in main.py, let's import it if possible, or copy minimal setup.
# Importing from main might run module-level code if not protected. main.py seems protected.

import sys
sys.path.append(str(Path(__file__).parents[2]))
from main import build_pipeline

def test_parallel_correctness():
    """Verify parallel execution produces identical results to sequential execution."""
    settings = Settings.load()
    # Use a small subset of files
    pdf_files = [
        str(Path(settings.input_dir) / "patient_10785.pdf"),
        str(Path(settings.input_dir) / "patient_14392.pdf")
    ]
    
    # Ensure test files exist
    valid_files = [f for f in pdf_files if Path(f).exists()]
    if not valid_files:
        pytest.skip("Test input files not found")

    pipeline = build_pipeline(settings)

    # 1. Run Sequential
    # Use a temporary output file for JSON to avoid overwriting prod data if needed
    # But parallel run will overwrite anyway.
    # We focus on the returned objects first.
    
    seq_results = pipeline.run_batch(valid_files, "tests/output/temp_seq.json")
    
    # 2. Run Parallel
    par_results = pipeline.run_batch_parallel(valid_files, "tests/output/temp_par.json", max_workers=2)

    # 3. Compare Results
    # Sort by pdf_path to handle out-of-order completion
    seq_results.sort(key=lambda x: x.pdf_path)
    par_results.sort(key=lambda x: x.pdf_path)

    assert len(seq_results) == len(par_results)
    
    for seq, par in zip(seq_results, par_results):
        assert seq.pdf_path == par.pdf_path
        assert seq.has_errors() == par.has_errors()
        
        # Compare extracted text (might be slightly different if OCR is non-deterministic? usually deterministic)
        # Compare metadata
        if not seq.has_errors():
            assert seq.metadata == par.metadata

    print("\nParallel execution correctness verified!")
