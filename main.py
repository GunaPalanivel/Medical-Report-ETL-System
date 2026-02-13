import sys
import traceback

from src.core import Settings, configure_logging, ensure_directory, get_pdf_files
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
from src.features.ocr import OCREngine, load_ocr_config
from src.features.output import JSONSerializer, PDFGenerator
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


def main() -> int:
    settings = Settings.load()
    logger = configure_logging(settings.log_level, settings.log_file)

    ensure_directory(settings.output_dir)
    pdf_files = get_pdf_files(settings.input_dir)
    if not pdf_files:
        raise ValueError(f"No PDF files found in {settings.input_dir}")

    logger.info("Processing %s PDF files", len(pdf_files))
    pipeline = build_pipeline(settings)
    results = pipeline.run_batch(pdf_files, settings.json_output)

    successes = sum(1 for item in results if not item.has_errors())
    failures = len(results) - successes

    print("=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Successfully processed: {successes} files")
    print(f"Failed: {failures} files")
    if failures:
        print("\nFailed files:")
        for context in results:
            if context.has_errors():
                print(f"  - {context.pdf_path}")
                for error in context.errors:
                    print(f"    * {error}")
    print("=" * 60)

    return 1 if failures else 0

# Entry point
if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
