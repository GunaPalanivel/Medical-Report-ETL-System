# Project Structure

**How the modular codebase is organized and why.**

---

## Directory Tree (v2.0.0)

```
Medical-Report-ETL-System/
│
├── src/                                    # Source code (modular)
│   │
│   ├── core/                              # 🏛️ CORE LAYER
│   │   │                                  #    Shared infrastructure
│   │   ├── config/
│   │   │   ├── __init__.py                # Config module exports
│   │   │   ├── settings.py                # Settings singleton (env-driven)
│   │   │   ├── env_loader.py              # Load .env into os.environ
│   │   │   └── profiles.py                # Environment profiles (dev/docker/prod)
│   │   │
│   │   ├── exceptions/
│   │   │   ├── __init__.py                # Exception hierarchy exports
│   │   │   ├── base.py                    # ETLException base class
│   │   │   ├── ocr.py                     # OCR-specific exceptions
│   │   │   ├── anonymization.py           # Anonymization exceptions
│   │   │   ├── extraction.py              # Extraction exceptions
│   │   │   └── output.py                  # Output exceptions
│   │   │
│   │   ├── logging/
│   │   │   ├── __init__.py                # Logging setup exports
│   │   │   ├── setup.py                   # Configure root logger
│   │   │   ├── formatters.py              # JSON formatter for logs
│   │   │   └── handlers.py                # Rotating file handler
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py                # Utils exports
│   │   │   ├── retry.py                   # @retry decorator
│   │   │   ├── validation.py              # Common validators
│   │   │   ├── file_utils.py              # Atomic write, path helpers
│   │   │   └── constants.py               # Shared constants
│   │   │
│   │   └── __init__.py
│   │
│   ├── features/                          # 🎯 FEATURE LAYER
│   │   │                                  #    Business capabilities (plugins)
│   │   ├── ocr/                           # ← Reads PDFs
│   │   │   ├── __init__.py
│   │   │   ├── engine.py                  # Main OCR orchestrator
│   │   │   ├── pdf_converter.py           # PDF → image conversion
│   │   │   ├── text_extractor.py          # Image → text via Tesseract
│   │   │   ├── config.py                  # OCR parameters (PSM, OEM)
│   │   │   └── validators.py              # Text validation
│   │   │
│   │   ├── anonymization/                 # ← Redacts PII
│   │   │   ├── __init__.py
│   │   │   ├── redactor.py                # Main redaction engine
│   │   │   ├── pii_patterns.py            # 🔌 PII pattern registry (8 patterns)
│   │   │   ├── uuid_service.py            # UUID generation & mapping
│   │   │   ├── validator.py               # Redaction verification
│   │   │   └── config.py                  # Redaction settings
│   │   │
│   │   ├── metadata/                      # ← Extracts fields
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py               # Main metadata coordinator
│   │   │   ├── extractors/                # 🔌 Pluggable extractors
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                # BaseExtractor interface
│   │   │   │   ├── gestational_age.py     # GA extractor (regex)
│   │   │   │   ├── demographics.py        # Age, BMI extractor
│   │   │   │   └── findings.py            # Findings extractor
│   │   │   ├── validators.py              # Field validators (range, type)
│   │   │   ├── schema.py                  # Metadata JSON schema
│   │   │   └── config.py                  # Extraction settings
│   │   │
│   │   ├── output/                        # ← Writes PDFs + JSON
│   │   │   ├── __init__.py
│   │   │   ├── pdf_generator.py           # Generate anonymized PDF
│   │   │   ├── json_serializer.py         # Serialize to JSON
│   │   │   ├── writers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── atomic_writer.py       # Atomic file writes
│   │   │   │   └── validator.py           # Output validation
│   │   │   └── config.py                  # Output settings
│   │   │
│   │   └── __init__.py
│   │
│   ├── pipeline/                          # 🔄 PIPELINE LAYER
│   │   │                                  #    Orchestration & stages
│   │   ├── __init__.py
│   │   ├── orchestrator.py                # ETLPipeline (20-line main class)
│   │   ├── context.py                     # PipelineContext (shared state)
│   │   ├── stages/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # BasePipelineStage interface
│   │   │   ├── ocr_stage.py               # Stage 1: OCR
│   │   │   ├── anonymization_stage.py     # Stage 2: Anonymization
│   │   │   ├── extraction_stage.py        # Stage 3: Extraction
│   │   │   └── output_stage.py            # Stage 4: Output
│   │   │
│   │   └── parallel/                      # ⏳ Phase 5: Multiprocessing
│   │       ├── __init__.py
│   │       ├── executor.py                # Parallel task executor
│   │       └── worker.py                  # Worker process
│   │
│   ├── pdf_handler.py                     # ⚠️ DEPRECATED
│   ├── anonymizer.py                      # ⚠️ DEPRECATED
│   ├── extractor.py                       # ⚠️ DEPRECATED
│   ├── json_writer.py                     # ⚠️ DEPRECATED
│   └── __init__.py
│
├── tests/                                 # 🧪 TEST SUITE (85%+ coverage)
│   ├── core/
│   │   ├── test_config.py                 # Config module tests
│   │   ├── test_exceptions.py             # Exception hierarchy tests
│   │   ├── test_utils.py                  # Utility function tests
│   │   └── test_logging.py                # Logging setup tests
│   │
│   ├── features/
│   │   ├── test_ocr.py                    # OCR feature tests
│   │   ├── test_anonymization.py          # Anonymization tests
│   │   ├── test_metadata.py               # Metadata extraction tests
│   │   └── test_output.py                 # Output generation tests
│   │
│   ├── pipeline/
│   │   └── test_orchestrator.py           # Pipeline orchestration tests
│   │
│   ├── integration/
│   │   └── test_end_to_end.py             # Full pipeline tests
│   │
│   ├── benchmarks/
│   │   ├── test_performance.py            # Performance benchmarks
│   │   └── test_memory.py                 # Memory usage tests
│   │
│   ├── fixtures/
│   │   ├── conftest.py                    # Pytest configuration
│   │   ├── sample_reports/                # Sample PDFs for testing
│   │   └── expected_outputs/              # Expected test outputs
│   │
│   └── __init__.py
│
├── docs/                                  # 📚 DOCUMENTATION
│   ├── SETUP.md                           # Local environment setup
│   ├── MODULAR_ARCHITECTURE.md            # Architecture deep-dive
│   ├── PROJECT_STRUCTURE.md               # This file
│   ├── DEVELOPMENT.md                     # Development workflow
│   ├── FEATURES.md                        # Feature reference
│   ├── PERFORMANCE.md                     # Performance guide
│   ├── HIPAA_COMPLIANCE.md                # Privacy & compliance
│   ├── DEPLOYMENT.md                      # Production deployment
│   └── REVISED_IMPLEMENTATION_PLAN.md     # 21-day roadmap
│
├── .github/
│   └── workflows/                         # ⏳ GitHub Actions (Phase 4)
│       ├── test.yml                       # Run tests on push
│       ├── lint.yml                       # Code quality checks
│       └── deploy.yml                     # Deploy to production
│
├── data/
│   ├── raw_reports/                       # INPUT: Scanned patient reports
│   ├── anonymized_reports/                # OUTPUT: Redacted PDFs
│   ├── patient_metadata.json              # OUTPUT: Structured metadata
│   └── id_map.json                        # OUTPUT: UUID mapping (🔒 .gitignore)
│
├── logs/
│   ├── etl.log                            # Application event log
│   └── error.log                          # Error log (errors only)
│
├── main.py                                # 🚀 Entry point (orchestrates pipeline)
├── requirements.txt                       # Python dependencies (pinned versions)
├── .env.example                           # Environment template
├── .gitignore                             # Git ignore patterns
├── CONTRIBUTING.md                        # Contributing guidelines
├── CHANGELOG.md                           # Version history
├── LICENSE                                # MIT license
└── README.md                              # Project overview
```

---

## Layer Responsibilities

### 🏛️ Core Layer (`src/core/`)

| Module        | Responsibility                       | What It Exports                      |
| ------------- | ------------------------------------ | ------------------------------------ |
| `config/`     | Load & manage configuration          | `Settings`, `EnvLoader`, `Profiles`  |
| `exceptions/` | Centralized exception hierarchy      | `ETLException`, domain-specific ones |
| `logging/`    | Structured logging setup             | `get_logger()`, JSON formatters      |
| `utils/`      | Shared utilities (retry, validation) | `@retry`, validators, file helpers   |

**Usage Rule:** Features + Pipeline import Core. Core imports nothing from Features/Pipeline.

### 🎯 Feature Layer (`src/features/`)

| Module           | Responsibility              | Plugin Points             |
| ---------------- | --------------------------- | ------------------------- |
| `ocr/`           | Extract text from PDFs      | (none - reads only)       |
| `anonymization/` | Redact PII from text        | `PIIPatternRegistry` (8+) |
| `metadata/`      | Extract clinical fields     | `BaseExtractor` interface |
| `output/`        | Write anonymized PDF + JSON | (none - writes only)      |

**Plugin Example:** Add new PII pattern without editing redactor.py

```python
# features/anonymization/pii_patterns.py
registry.register(PIIPattern(
    name="custom_field",
    regex=r"<your_regex>",
    replacement="[REDACTED]"
))
```

### 🔄 Pipeline Layer (`src/pipeline/`)

| Module         | Responsibility                          |
| -------------- | --------------------------------------- |
| `orchestrator` | Coordinate 4 stages, manage context     |
| `context`      | Carry state between pipeline stages     |
| `stages/`      | Individual processing stages (OCR, etc) |
| `parallel/`    | Multiprocessing executor (Phase 5)      |

**Stage Pattern:** Each stage is testable independently

```python
# Example: Add new stage
class CustomStage(BasePipelineStage):
    def execute(self, context: PipelineContext) -> PipelineContext:
        # Process context, return updated context
        return context
```

---

## Import Rules (Prevent Circular Dependencies)

✅ **Allowed:**

```python
# Features can import Core
from src.core.exceptions import ETLException
from src.core.logging import get_logger

# Pipeline can import Features + Core
from src.features.ocr import OCREngine
from src.core.config import Settings

# Pipeline orchestrates Stages (same layer)
from src.pipeline.stages import OCRStage, AnonymizationStage
```

❌ **NOT Allowed:**

```python
# Core should NOT import Features/Pipeline
from src.features.ocr import OCREngine  # ← Don't do this in core/

# Features should NOT import other Features at top level
from src.features.anonymization import Redactor  # ← Bad dependency

# Pipeline should NOT import main.py or create circular deps
```

---

## File Naming Conventions

| Pattern          | Example                        | Purpose                   |
| ---------------- | ------------------------------ | ------------------------- |
| `*_engine.py`    | `ocr_engine.py`                | Main orchestrator         |
| `*_service.py`   | `uuid_service.py`              | Service/utility           |
| `*_stage.py`     | `ocr_stage.py`                 | Pipeline stage            |
| `*_extractor.py` | `gestational_age_extractor.py` | Pluggable extractor       |
| `*_validator.py` | `redaction_validator.py`       | Validates specific output |
| `test_*.py`      | `test_ocr.py`                  | Test file                 |
| `__init__.py`    | Every package                  | Package exports           |

---

## Key Files to Know

### Entry Points

| File                                                              | Purpose        | Typical Usage                  |
| ----------------------------------------------------------------- | -------------- | ------------------------------ |
| [`main.py`](../main.py)                                           | Start here     | `python main.py` runs pipeline |
| [`src/pipeline/orchestrator.py`](../src/pipeline/orchestrator.py) | Pipeline logic | `ETLPipeline().run()`          |

### Configuration

| File                                                            | Purpose                            |
| --------------------------------------------------------------- | ---------------------------------- |
| [`.env.example`](../.env.example)                               | Template for environment variables |
| [`src/core/config/settings.py`](../src/core/config/settings.py) | Loads & exposes settings           |

### Critical Files to Protect

| File               | Why                        | Action              |
| ------------------ | -------------------------- | ------------------- |
| `data/id_map.json` | Contains PII mapping       | Add to `.gitignore` |
| `.env`             | Passwords, paths           | Never commit to Git |
| `logs/etl.log`     | May contain sensitive data | Rotate regularly    |

---

## Quick Navigation

**Want to understand:**

- Architecture → [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)
- How to add PII pattern → [DEVELOPMENT.md](DEVELOPMENT.md#adding-pii-patterns)
- How to add extractor → [DEVELOPMENT.md](DEVELOPMENT.md#adding-extractors)
- Performance settings → [PERFORMANCE.md](PERFORMANCE.md)
- Compliance requirements → [HIPAA_COMPLIANCE.md](HIPAA_COMPLIANCE.md)

---

## Why This Structure?

✅ **Single Responsibility:** Each module has one job  
✅ **Testable:** Features can be tested independently  
✅ **Extensible:** Plugins without editing existing code  
✅ **Maintainable:** New devs can find code quickly  
✅ **Scalable:** Can add parallel processing without refactoring
