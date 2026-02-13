# Migration Guide: v1.x to v2.0.0

The v2.0.0 release introduces a modular architecture to improve maintainability, testability, and extensibility. This guide helps you migrate your existing installation and custom code.

## Key Changes

- **Monolithic to Modular**: Logic is now split into `src/core`, `src/features`, and `src/pipeline`.
- **Configuration**: `Settings` class in `src/core/config` now handles all configuration.
- **Pipeline**: Explicit pipeline stages (`OCRStage`, `AnonymizationStage`, etc.) replace the monolithic script.
- **Plugin System**: PII patterns and Metadata extractors are now registered via plugins.

## 1. Upgrading Code

### If you use `main.py` directly:
No changes needed. The CLI interface remains the same.
```bash
python main.py
```

### If you import modules in your scripts:
The old modules (`pdf_handler.py`, `anonymizer.py`, `extractor.py`, `json_writer.py`) are **deprecated** but kept for backward compatibility. They will emit warnings and will be removed in v3.0.0.

**v1.x Import (Deprecated):**
```python
from src.pdf_handler import read_pdf_text
from src.anonymizer import anonymize_report
from src.extractor import extract_metadata
```

**v2.0.0 Import (Recommended):**
```python
from src.features.ocr import OCREngine
from src.features.anonymization import PIIRedactor
from src.features.metadata import MetadataExtractor

# See src/pipeline/orchestrator.py for usage examples
```

## 2. Configuration Changes

Ensure your `.env` file is up to date. New options may be available (e.g., logging levels), but old keys (`TESSERACT_PATH`, `POPPLER_PATH`) are fully supported.

## 3. Custom Extensions

### Adding a new PII Pattern
**v1.x**: You had to modify `src/anonymizer.py` regex list.
**v2.0**: Register a new pattern in `src/features/anonymization/pii_patterns.py` or at runtime:

```python
from src.features.anonymization import PIIPattern, registry

registry.register(PIIPattern(
    name="custom_id",
    regex=r"ID-\d+",
    replacement="[REDACTED]"
))
```

### Adding a Metadata Extractor
**v1.x**: Modify `src/extractor.py`.
**v2.0**: Implement `BaseExtractor` in `src/features/metadata/extractors/` and add it to the `MetadataExtractor` list in `main.py`.

## 4. Troubleshooting

- **ImportError**: Make sure you are running from the project root.
- **Logs**: Check `logs/pipeline.log` for structured JSON logs.
