# Modular Architecture (v2.0.0)

**Feature-based design, plugin system, and extensibility.**

---

## Architecture Philosophy

### Problem: Spaghetti Code (v1.0.0)

**What went wrong:**

```
❌ Old v1.0.0:
  - pdf_handler.py: Did BOTH reading AND writing (mixed responsibility)
  - anonymizer.py: Only 4 hardcoded PII patterns (not extensible)
  - extractor.py: Monolithic, hard to test independently
  - main.py: 60+ lines of procedural code (hard to understand)
```

**Consequences:**

- 🚫 Adding a new PII pattern required editing 3 files
- 🚫 Hard to test anonymization without PDF logic
- 🚫 Tight coupling = brittle code
- 🚫 New developers can't find code quickly

### Solution: Feature-Based Modular Design (v2.0.0)

**What's better:**

```
✅ New v2.0.0:
  - ocr/: Only reads PDFs (single responsibility)
  - anonymization/: Only redacts PII (plugin system for 8 patterns)
  - metadata/: Only extracts fields (pluggable extractors)
  - output/: Only writes PDFs + JSON (atomic writes)
  - pipeline/: Orchestrates the stages (20-line main.py)
```

**Benefits:**

- ✅ Add new PII pattern in 5 minutes (just register)
- ✅ Test anonymization independently
- ✅ Clear boundaries = easy to maintain
- ✅ New developers understand structure immediately

---

## 4-Layer Architecture

### Layer 1: Pipeline (Orchestration)

**What it does:** Coordinate the 4 processing stages.

**Files:**

- `pipeline/orchestrator.py` — Main ETLPipeline class
- `pipeline/context.py` — Shared state between stages
- `pipeline/stages/` — Individual stage implementations

**Example:**

```python
# src/pipeline/orchestrator.py
class ETLPipeline:
    def process_reports(self, pdf_paths: List[str]):
        context = PipelineContext()

        for pdf_path in pdf_paths:
            context.pdf_path = pdf_path

            # Stage 1: Extract text
            ocr_stage = OCRStage()
            context = ocr_stage.execute(context)

            # Stage 2: Redact PII
            anon_stage = AnonymizationStage()
            context = anon_stage.execute(context)

            # Stage 3: Extract metadata
            extract_stage = ExtractionStage()
            context = extract_stage.execute(context)

            # Stage 4: Write outputs
            output_stage = OutputStage()
            context = output_stage.execute(context)
```

**Why this layer?**

- Clean separation of concerns
- Easy to add/remove stages
- Testable in isolation

---

### Layer 2: Features (Business Logic)

**What it does:** Actual clinical/processing logic grouped by capability.

**Four Feature Domains:**

#### 🔍 OCR Feature (`features/ocr/`)

**Responsibility:** Extract text from PDF images

```python
# src/features/ocr/engine.py
class OCREngine:
    def extract_text(self, pdf_path: str) -> str:
        """Convert PDF → images → text"""
        images = self.pdf_to_images(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
```

**Files:**

- `engine.py` — Main orchestrator
- `pdf_converter.py` — PDF → images
- `text_extractor.py` — Image → text
- `config.py` — OCR parameters (PSM, language)
- `validators.py` — Verify extracted text

**Plugin Points:** None (reads only)

---

#### 🔐 Anonymization Feature (`features/anonymization/`)

**Responsibility:** Redact PII from text

```python
# src/features/anonymization/redactor.py
class Redactor:
    def __init__(self, registry: PIIPatternRegistry):
        self.patterns = registry.patterns

    def redact(self, text: str) -> str:
        """Apply all PII patterns"""
        for pattern in self.patterns.values():
            text = re.sub(pattern.regex, pattern.replacement, text)
        return text
```

**Files:**

- `redactor.py` — Main redaction engine
- `pii_patterns.py` — 🔌 **Plugin registry** (8 patterns, easily extended)
- `uuid_service.py` — UUID mapping
- `validator.py` — Verify redaction
- `config.py` — Redaction settings

**Plugin Points:**

```python
# Add new PII pattern (no editing of redactor.py needed)
from src.features.anonymization.pii_patterns import registry, PIIPattern

registry.register(PIIPattern(
    name="ssn",
    regex=r"\b\d{3}-\d{2}-\d{4}\b",
    replacement="[SSN REDACTED]"
))
```

---

#### 📝 Metadata Feature (`features/metadata/`)

**Responsibility:** Extract clinical fields from text

```python
# src/features/metadata/extractor.py
class MetadataExtractor:
    def __init__(self):
        self.extractors = [
            GestationalAgeExtractor(),
            DemographicsExtractor(),
            FindingsExtractor(),
            # Add more here
        ]

    def extract_all(self, text: str) -> dict:
        """Run all extractors"""
        metadata = {}
        for extractor in self.extractors:
            value = extractor.extract(text)
            if value and extractor.validate(value):
                metadata[extractor.field_name] = value
        return metadata
```

**Files:**

- `extractor.py` — Main coordinator
- `extractors/base.py` — 🔌 **BaseExtractor interface**
- `extractors/gestational_age.py` — Extract GA
- `extractors/demographics.py` — Extract age, BMI
- `extractors/findings.py` — Extract clinical findings
- `schema.py` — JSON schema validation
- `validators.py` — Field validators

**Plugin Points:**

```python
# Add new extractor (just implement interface)
from src.features.metadata.extractors.base import BaseExtractor

class BloodPressureExtractor(BaseExtractor):
    def extract(self, text: str) -> Optional[str]:
        match = re.search(r"BP[:\s]+(\d+/\d+)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def validate(self, value: str) -> bool:
        systolic, diastolic = map(int, value.split('/'))
        return 80 <= systolic <= 200 and 40 <= diastolic <= 130

    @property
    def field_name(self) -> str:
        return "blood_pressure"

# Register it
extractor.extractors.append(BloodPressureExtractor())
```

---

#### 📁 Output Feature (`features/output/`)

**Responsibility:** Write anonymized PDF + JSON

```python
# src/features/output/pdf_generator.py
class PDFGenerator:
    def generate(self, anonymized_text: str, output_path: str):
        """Generate anonymized PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, anonymized_text)
        pdf.output(output_path)

# src/features/output/json_serializer.py
class JSONSerializer:
    def serialize(self, metadata: dict, output_path: str):
        """Append metadata to JSON"""
        existing = self._read_json()
        existing['dataResources'].append(metadata)
        self._write_json_atomic(existing, output_path)
```

**Files:**

- `pdf_generator.py` — Generate PDF
- `json_serializer.py` — Generate JSON
- `writers/` — File I/O (atomic writes)
- `config.py` — Output settings
- `validators.py` — Output validation

**Plugin Points:** None (writes only)

---

### Layer 3: Core (Infrastructure)

**What it does:** Shared utilities used by all features.

**Four Core Submodules:**

| Module        | Purpose                  | Example                                |
| ------------- | ------------------------ | -------------------------------------- |
| `config/`     | Configuration management | Load .env, settings singleton          |
| `exceptions/` | Exception hierarchy      | ETLException + domain-specific         |
| `logging/`    | Structured logging       | JSON formatter, rotating file handler  |
| `utils/`      | Utility functions        | @retry decorator, validators, file ops |

**Example:**

```python
# src/core/config/settings.py
class Settings:
    def __init__(self):
        self.tesseract_path = os.getenv('TESSERACT_PATH')
        self.workers = int(os.getenv('WORKERS', 1))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()  # Singleton

# src/core/logging/setup.py
logger = get_logger(__name__)
logger.info("Pipeline started", extra={'duration_ms': 5234})

# src/core/utils/retry.py
@retry(max_attempts=3, backoff_factor=2)
def extract_text(pdf_path: str) -> str:
    # Automatically retries on failure
    pass
```

**Import Rule:** Core imports nothing from Features/Pipeline (no circles)

---

### Layer 4: Tests (Quality Assurance)

**What it does:** Verify each layer works correctly.

**Test Structure:**

```
tests/
├── core/                        # Core layer tests
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_logging.py
│   └── test_utils.py
├── features/                    # Feature layer tests
│   ├── test_ocr.py              # OCR engine tests
│   ├── test_anonymization.py    # Redactor + patterns
│   ├── test_metadata.py         # Extractors + schema
│   └── test_output.py           # PDF + JSON generation
├── pipeline/                    # Pipeline tests
│   └── test_orchestrator.py     # Stage orchestration
├── integration/                 # End-to-end tests
│   └── test_end_to_end.py       # Full pipeline
└── fixtures/                    # Test data
    ├── sample_reports/          # Sample PDFs
    └── expected_outputs/        # Known results
```

**Coverage Goals:**

- Core: 90%+
- Features: 90%+
- Pipeline: 85%+
- Overall: 85%+

---

## Data Flow Through Layers

```
Input (raw PDF)
      │
      ▼
┌─────────────────────────────────────────────────┐
│            PIPELINE LAYER                       │
│  pipeline/orchestrator.py                       │
│  "Coordinate 4 stages"                          │
└──────────────────┬────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│ Stage 1 │  │ Stage 2  │  │ Stage 3  │
│(OCRStage)  │(AnonymizationStage)    │(ExtractionStage)
└────┬────┘  └────┬─────┘  └────┬─────┘
     │            │            │
     ▼            ▼            ▼
┌────────────────────────────────────────────────┐
│          FEATURE LAYER                         │
│ ocr/engine → anonymization/redactor → metadata│
│          /extractor                           │
└────────────────────────────┬───────────────────┘
                             │
                             ▼
                        ┌──────────────┐
                        │ Stage 4      │
                        │(OutputStage) │
                        └────┬─────────┘
                             │
                             ▼
                        features/output/
                        pdf_generator +
                        json_serializer
                             │
                             ▼
┌────────────────────────────────────────┐
│      CORE LAYER (Below All)            │
│ config/ → exceptions/ → logging/ →    │
│           utils/                      │
└────────────────────────────────────────┘

Output (anonymized PDF + JSON)
```

---

## Design Patterns Used

### 1. Pipeline Pattern

Process data through sequential stages:

```python
class BasePipelineStage(ABC):
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        pass

class OCRStage(BasePipelineStage):
    def execute(self, context: PipelineContext) -> PipelineContext:
        ocr = OCREngine()
        context.extracted_text = ocr.extract_text(context.pdf_path)
        return context
```

**Benefits:** Stages are testable independently, reorderable, extensible

### 2. Registry Pattern (Plugins)

Allow runtime registration of components:

```python
class PIIPatternRegistry:
    def __init__(self):
        self.patterns = {}

    def register(self, pattern: PIIPattern):
        self.patterns[pattern.name] = pattern

registry = PIIPatternRegistry()

# Register at startup
registry.register(PIIPattern(name="ssn", regex=..., replacement=...))
```

**Benefits:** Add patterns without editing redactor.py

### 3. Strategy Pattern (Extractors)

Different extraction strategies with common interface:

```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> Optional[str]:
        pass

class GestationalAgeExtractor(BaseExtractor):
    def extract(self, text: str) -> Optional[str]:
        # GA-specific regex
        pass

class DemographicsExtractor(BaseExtractor):
    def extract(self, text: str) -> Optional[str]:
        # Age/BMI-specific regex
        pass
```

**Benefits:** Add extractors without editing main coordinator

### 4. Singleton Pattern (Configuration)

One global settings object:

```python
from src.core.config.settings import settings

# Access anywhere
tesseract_path = settings.tesseract_path
workers = settings.workers
```

**Benefits:** Centralized config, environment-driven

### 5. Facade Pattern (Backward Compatibility)

Old API calls new code:

```python
# Old API (deprecated but works)
from src import anonymizer
result = anonymizer.write_anonymized_pdf(text)

# Maps to new code (no change needed by users)
# src/anonymizer.py (facade)
from src.features.output.pdf_generator import PDFGenerator

def write_anonymized_pdf(text):
    gen = PDFGenerator()
    return gen.generate(text)
```

**Benefits:** Smooth migration from v1.0.0 to v2.0.0

---

## Dependency Graph

```
           main.py
              │
              ▼
    pipeline/orchestrator.py ──────┐
              │                    │
              ├─────────────┐      │
              │             │      │
              ▼             ▼      │
    pipeline/stages/     PipelineContext
              │             │      │
    OCRStage  │      │      │      │
    AnonymStage──────┘      │      │
    ExtractStage            │      │
    OutputStage             │      │
              │             │      │
              └─────────────┼──────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    features/ocr/    features/anonymization/ features/metadata/
    features/output/
           │                │                │
           └────────────────┼────────────────┘
                            │
                     IMPORTS FROM CORE
                            │
                 ┌──────────┬┴────────┬─────────┐
                 ▼          ▼         ▼         ▼
            core/config/  core/exceptions/  core/logging/  core/utils/
```

**Rule:** No backward arrows (acyclic dependencies)

---

## Extending the System

### Add New PII Pattern

**Time:** 5 minutes | **Code:** 3 lines

```python
# 1. Define pattern
registry.register(PIIPattern(
    name="phone",
    regex=r"(\+?1)?[-.\s]?\(?([0-9]{3})\)?...",
    replacement="[PHONE REDACTED]"
))

# 2. Test (optional)
# pytest tests/features/test_anonymization.py::test_phone -v

# 3. Done! Automatically used in pipeline
```

### Add New Metadata Extractor

**Time:** 30 minutes | **Code:** ~40 lines

```python
# 1. Create extractor class
class BloodPressureExtractor(BaseExtractor):
    def extract(self, text: str) -> Optional[str]:
        match = re.search(r"BP[:\s]+(\d+/\d+)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def validate(self, value: str) -> bool:
        systolic, diastolic = map(int, value.split('/'))
        return 80 <= systolic <= 220 and 40 <= diastolic <= 130

    @property
    def field_name(self) -> str:
        return "blood_pressure"

# 2. Register in coordinator
extractor.extractors.append(BloodPressureExtractor())

# 3. Test
# pytest tests/features/test_metadata.py -v

# 4. Done! Automatically extracted in pipeline
```

### Add New Pipeline Stage

**Time:** 1 hour | **Code:** ~100 lines

```python
# 1. Create stage class
class ValidatorStage(BasePipelineStage):
    def execute(self, context: PipelineContext) -> PipelineContext:
        # Validate extracted metadata
        validator = JSONValidator()
        context.validation_result = validator.validate(context.metadata)
        return context

# 2. Add to orchestrator
pipeline.stages.append(ValidatorStage())

# 3. Test
# pytest tests/pipeline/ -v

# 4. Done! New stage automatically integrated
```

---

## Why This Design Beats Spaghetti Code

| Aspect                    | Spaghetti (v1.0.0)             | Modular (v2.0.0)                             |
| ------------------------- | ------------------------------ | -------------------------------------------- |
| **Adding PII pattern**    | Edit 3 files (30 min)          | Edit 1 file (5 min)                          |
| **Testing anonymization** | Must setup PDFs, OCR (complex) | Just test redactor function                  |
| **Code navigation**       | Where is PII logic? (unclear)  | `features/anonymization/redactor.py` (clear) |
| **Reusing OCR**           | Tightly coupled to PDF handler | Import `OCREngine` directly                  |
| **Adding extractor**      | Monolithic, requires refactor  | Implement interface, register (30 min)       |
| **Testing new feature**   | Cannot run tests in isolation  | Each feature independently testable          |
| **Performance tuning**    | Change impacts whole system    | Optimize specific stage only                 |
| **Documentation**         | "Read the code"                | Clear boundaries, self-documenting           |

---

## Next Steps

- 🏗️ Setting up? Start with [SETUP.md](SETUP.md)
- 🔨 Adding features? See [DEVELOPMENT.md](DEVELOPMENT.md)
- 📊 Understand the codebase? See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- 🚀 Ready for production? See [DEPLOYMENT.md](DEPLOYMENT.md)
