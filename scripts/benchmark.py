import argparse
import sys
import time
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.core import Settings, configure_logging, get_pdf_files
from src.features.ocr import OCREngine, load_ocr_config
from src.features.anonymization import (
    PIIRedactor,
    RedactionValidator,
    UUIDMappingService,
    build_default_registry,
)
from src.features.metadata import (
    AgeExtractor,
    BMIExtractor,
    FindingsExtractor,
    GestationalAgeExtractor,
    MetadataExtractor,
)
from src.features.output import PDFGenerator, JSONSerializer
from src.pipeline import (
    AnonymizationStage,
    ETLPipeline,
    ExtractionStage,
    OCRStage,
    OutputStage,
)

def build_pipeline(settings: Settings) -> ETLPipeline:
    ocr_config = load_ocr_config(settings)
    ocr_engine = OCREngine(ocr_config)

    registry = build_default_registry()
    patterns = registry.get_all()
    redactor = PIIRedactor(patterns)
    validator = RedactionValidator(patterns)

    extractor = MetadataExtractor(
        [
            GestationalAgeExtractor(),
            AgeExtractor(),
            BMIExtractor(),
            FindingsExtractor(),
        ]
    )

    pdf_generator = PDFGenerator()
    uuid_service = UUIDMappingService(settings.id_map_file)
    json_serializer = JSONSerializer()

    stages = [
        OCRStage(ocr_engine),
        AnonymizationStage(redactor, validator),
        ExtractionStage(extractor),
        OutputStage(pdf_generator, uuid_service, settings.output_dir),
    ]

    return ETLPipeline(stages, json_serializer)

def run_benchmark(limit: int = None, parallel: bool = False, workers: int = None):
    settings = Settings.load()
    # Disable file logging for benchmark to avoid I/O noise, or keep it?
    # Keeping it as it reflects production usage.
    configure_logging(settings.log_level, settings.log_file)
    
    print(f"Loading PDFs from: {settings.input_dir}")
    pdf_files = get_pdf_files(settings.input_dir)
    
    if limit:
        pdf_files = pdf_files[:limit]
        print(f"Limiting to first {limit} files.")
    
    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Processing {len(pdf_files)} files...")
    pipeline = build_pipeline(settings)
    
    start_time = time.time()
    
    if parallel:
        if hasattr(pipeline, 'run_batch_parallel'):
            print(f"Running in PARALLEL mode with {workers} workers...")
            results = pipeline.run_batch_parallel(pdf_files, settings.json_output, max_workers=workers)
        else:
            print("Error: run_batch_parallel not implemented yet.")
            return
    else:
        print("Running in SEQUENTIAL mode...")
        results = pipeline.run_batch(pdf_files, settings.json_output)
        
    end_time = time.time()
    duration = end_time - start_time
    
    success_count = sum(1 for r in results if not r.has_errors())
    avg_time = duration / len(pdf_files) if pdf_files else 0
    throughput = len(pdf_files) / duration if duration > 0 else 0
    
    print("\n" + "="*40)
    print("BENCHMARK RESULTS")
    print("="*40)
    print(f"Mode:           {'Parallel' if parallel else 'Sequential'}")
    print(f"Files:          {len(pdf_files)}")
    print(f"Success:        {success_count}")
    print(f"Total Time:     {duration:.2f}s")
    print(f"Avg Time/PDF:   {avg_time:.2f}s")
    print(f"Throughput:     {throughput:.2f} PDFs/sec")
    print("="*40 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark ETL Pipeline")
    parser.add_argument("--limit", type=int, help="Limit number of PDFs to process")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    parser.add_argument("--workers", type=int, help="Number of workers for parallel processing")
    
    args = parser.parse_args()
    
    run_benchmark(limit=args.limit, parallel=args.parallel, workers=args.workers)
