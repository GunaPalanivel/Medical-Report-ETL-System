# Modular Refactoring Guide (v1.0 → v2.0)

**Step-by-step instructions for transforming spaghetti code → modular architecture**

---

## Overview

This guide walks you through 10 days of refactoring to transform your Medical Report ETL system from v1.0.0 (monolithic) to v2.0.0 (modular/feature-based).

### Timeline

```
TODAY         Phase 0: Hotfix (4 hours) — Fix critical bugs
Tomorrow      Phase 1: Infrastructure (Days 1-3) — Build core/
Wed-Thu       Phase 2: Features (Days 4-7) — Build features/
Fri-Sat       Phase 3: Pipeline (Days 8-10) — Build pipeline/
            Phase 4: Backward Compatibility (Days 11-12) — Old API still works
            Phase 5: Testing (Days 13-15) — Achieve 85%+ coverage
            Phase 6: Deployment (Days 16-20) — Production-ready
```

---

## Right Now: Phase 0 (Emergency Hotfix) — 4 HOURS

### Critical Bugs to Fix

| Bug                                         | Impact                        | Fix                               |
| ------------------------------------------- | ----------------------------- | --------------------------------- |
| `write_anonymized_pdf()` signature mismatch | System crashes on PDF output  | Update signature to match callers |
| `gestaional_age` → `gestational_age` typo   | Metadata extraction fails     | Rename field everywhere           |
| Missing error handlers                      | Crashes on bad PDFs           | Add try/except in main.py         |
| `.gitignore` missing `id_map.json`          | Expose patient maps to GitHub | Add to .gitignore                 |

### Step 1: Fix PDF Signature Mismatch (30 min)

**Current broken code:**

```python
# src/pdf_handler.py
def write_anonymized_pdf(text: str, output_path: str) -> None:
    # Current signature

# main.py calls it as:
pdf_handler.write_anonymized_pdf(anonymized_text, output_path)  # ✅ Works
```

**Check callers:**

```bash
cd d:\Projects\Medical Report ETL System
grep -r "write_anonymized_pdf" src/ main.py
```

**Fix:** Ensure all callers use consistent signature. If signature is actually wrong, update to:

```python
def write_anonymized_pdf(text: str, output_path: str) -> None:
    """Generate anonymized PDF file"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)
```

### Step 2: Fix Typo (20 min)

**Find the typo:**

```bash
# PowerShell
Get-ChildItem -Path "d:\Projects\Medical Report ETL System\src" -File -Recurse |
    Select-String "gestaional"
```

**Fix:**

```python
# Before
def extract_gestational_age(text: str) -> dict:
    return {"gestaional_age": value}  # ❌ Typo

# After
def extract_gestational_age(text: str) -> dict:
    return {"gestational_age": value}  # ✅ Fixed
```

**Update all references:**

```bash
# In all Python files
Find: "gestaional_age"
Replace: "gestational_age"
```

### Step 3: Add Error Handling (60 min)

**Update main.py:**

```python
import sys
import traceback
from pathlib import Path

def main():
    """Main entry point with error handling"""
    try:
        # 1. Load configuration
        config = load_config()

        # 2. Validate input directory
        input_dir = Path(config['input_dir'])
        if not input_dir.exists():
            raise ValueError(f"Input directory not found: {input_dir}")

        # 3. Get PDFs
        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {input_dir}")

        # 4. Process each PDF with per-file error handling
        results = {'success': 0, 'errors': 0}
        for pdf_path in pdf_files:
            try:
                process_report(pdf_path, config)
                results['success'] += 1
            except Exception as e:
                print(f"❌ Error processing {pdf_path.name}: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                results['errors'] += 1
                continue  # Continue with next file

        # 5. Summary
        print(f"✅ Processed {results['success']} files successfully")
        if results['errors'] > 0:
            print(f"⚠️  {results['errors']} files had errors")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def process_report(pdf_path: Path, config: dict) -> dict:
    """Process single report with error handling"""
    # 1. OCR
    try:
        text = pdf_handler.extract_text(str(pdf_path))
    except Exception as e:
        raise ValueError(f"OCR failed for {pdf_path.name}: {e}")

    # 2. Anonymize
    try:
        anonymized_text = anonymizer.anonymize(text)
    except Exception as e:
        raise ValueError(f"Anonymization failed for {pdf_path.name}: {e}")

    # 3. Extract metadata
    try:
        metadata = extractor.extract_metadata(anonymized_text)
    except Exception as e:
        raise ValueError(f"Metadata extraction failed for {pdf_path.name}: {e}")

    # 4. Write outputs
    try:
        output_pdf = Path(config['output_dir']) / f"anon_{pdf_path.name}"
        pdf_handler.write_anonymized_pdf(anonymized_text, str(output_pdf))

        json_writer.append_to_json(metadata, config['json_output'])
    except Exception as e:
        raise ValueError(f"Output writing failed for {pdf_path.name}: {e}")

    return {'success': True, 'pdf': str(pdf_path), 'metadata': metadata}

if __name__ == "__main__":
    main()
```

### Step 4: Update .gitignore (10 min)

**Create/update .gitignore:**

```
# .gitignore

# 🔐 Patient data (NEVER commit)
data/id_map.json
data/patient_metadata.json

# Raw reports (optional, can be large)
data/raw_reports/
data/anonymized_reports/

# Python
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
venv/
env/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

**Verify (CRITICAL!):**

```bash
# PowerShell - Check NO secrets will be committed
git status

# Make sure to see:
# ?? .gitignore  (new file)
# But NOT:
# ?? data/id_map.json (should be ignored)
```

### Test Phase 0 Completion (30 min)

```bash
cd d:\Projects\Medical Report ETL System

# 1. Run on 3 sample PDFs (ensure 0 crashes)
python main.py

# Expected output:
# ✅ Processed 3 files successfully

# 2. Verify outputs exist
ls anonymized_reports/  # Should have 3 PDFs
ls data/output.json     # Should have metadata

# 3. Verify id_map.json is in .gitignore
cat .gitignore | grep "id_map.json"  # Should show line

# 4. Quick code review
#    - Check main.py has error handling
#    - Check gestational_age (not gestaional)
#    - Check PDF writer exists
```

**Phase 0 Complete!** Now ready for modular refactoring.

---

## Phase 1: Build Infrastructure Layer (Days 1-3)

### Goal

Create `src/core/` — reusable utilities that other layers depend on.

### Day 1: Create Core/Config + Exceptions

```python
# src/core/__init__.py
"""Core infrastructure layer"""

# src/core/config/__init__.py
from .settings import settings

__all__ = ['settings']

# src/core/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    """Global configuration (singleton)"""

    def __init__(self):
        load_dotenv()

        # Paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.input_dir = self.data_dir / "raw_reports"
        self.output_dir = self.data_dir / "anonymized_reports"
        self.json_output = self.data_dir / "output.json"
        self.id_map_file = self.data_dir / "id_map.json"

        # OCR settings
        self.tesseract_path = os.getenv('TESSERACT_PATH', 'tesseract')
        self.poppler_path = os.getenv('POPPLER_PATH', '')
        self.ocr_dpi = int(os.getenv('OCR_DPI', 300))
        self.ocr_language = os.getenv('OCR_LANGUAGE', 'eng')

        # Processing settings
        self.workers = int(os.getenv('WORKERS', 1))
        self.batch_size = int(os.getenv('BATCH_SIZE', 50))

        # Output settings
        self.anonymized_metadata = os.getenv('ANONYMIZED_METADATA', 'true').lower() == 'true'

        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = self.base_dir / 'logs' / 'pipeline.log'

        # Validation
        self._validate()

    def _validate(self):
        """Validate required settings"""
        if not self.input_dir.exists():
            raise ValueError(f"Input dir not found: {self.input_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / 'logs').mkdir(exist_ok=True)

# Use it anywhere:
from src.core.config import settings
print(settings.ocr_dpi)  # 300
```

**Create exceptions:**

```python
# src/core/exceptions/__init__.py
"""Domain-specific exceptions"""

class ETLException(Exception):
    """Base exception for ETL system"""
    pass

class OcrException(ETLException):
    """OCR-related errors"""
    pass

class AnonymizationException(ETLException):
    """Anonymization-related errors"""
    pass

class MetadataException(ETLException):
    """Metadata extraction errors"""
    pass

class OutputException(ETLException):
    """Output generation errors"""
    pass
```

### Day 2: Create Core/Logging + Utils

**Structured logging:**

```python
# src/core/logging/__init__.py
import logging
import json
from pathlib import Path
from src.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """Get configured logger"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console)

        # File handler (rotating)
        (settings.log_file.parent).mkdir(exist_ok=True)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        logger.setLevel(getattr(logging, settings.log_level))

    return logger
```

**Utility decorators:**

```python
# src/core/utils/__init__.py
from .retry import retry
from .validators import validate_not_empty, validate_path
from .file_ops import ensure_dir, atomic_write

__all__ = ['retry', 'validate_not_empty', 'validate_path', 'ensure_dir', 'atomic_write']

# src/core/utils/retry.py
import time
from functools import wraps
from src.core.logging import get_logger

logger = get_logger(__name__)

def retry(max_attempts: int = 3, backoff_factor: float = 2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    wait = backoff_factor ** (attempt - 1)
                    logger.warning(f"Attempt {attempt} failed. Retrying in {wait}s: {e}")
                    time.sleep(wait)
        return wrapper
    return decorator

# src/core/utils/validators.py
def validate_not_empty(value, field_name: str) -> str:
    """Ensure value is not empty"""
    if not value or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{field_name} cannot be empty")
    return value

def validate_path(path_str: str) -> Path:
    """Ensure path exists"""
    from pathlib import Path
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    return path

# src/core/utils/file_ops.py
import json
import tempfile
from pathlib import Path

def ensure_dir(path: Path):
    """Create directory if needed"""
    path.mkdir(parents=True, exist_ok=True)

def atomic_write(data: dict, output_path: str):
    """Write JSON atomically (write to temp, then move)"""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    # Write to temp file first
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        dir=output_path.parent,
        delete=False
    ) as f:
        json.dump(data, f, indent=2)
        temp_path = f.name

    # Atomic rename
    Path(temp_path).replace(output_path)
```

### Day 3: Fix Import Paths

Add `src/` to Python path so imports work:

```python
# src/__init__.py
"""Medical Report ETL - Modular Architecture v2.0.0"""
__version__ = "2.0.0"

# main.py - Add at top
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Then imports work:
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import ETLException
```

**Verify Phase 1:**

```bash
# Test imports work
python -c "from src.core.config import settings; print(settings.ocr_dpi)"
# Expected: 300

# Test logging works
python -c "from src.core.logging import get_logger; logger = get_logger('test'); logger.info('Works')"
```

---

## Phase 2: Refactor Features (Days 4-7)

### Goal

Create `src/features/` — extract business logic from monolithic files into pluggable features.

### Day 4: Create OCR Feature

**Extract OCR logic from pdf_handler.py:**

```python
# src/features/ocr/__init__.py
from .engine import OCREngine

__all__ = ['OCREngine']

# src/features/ocr/engine.py
from pathlib import Path
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import OcrException
from .pdf_converter import PDFToImages
from .text_extractor import ImageToText

logger = get_logger(__name__)

class OCREngine:
    """Extract text from PDF files"""

    def __init__(self):
        self.pdf_converter = PDFToImages(
            poppler_path=settings.poppler_path
        )
        self.text_extractor = ImageToText(
            tesseract_path=settings.tesseract_path,
            language=settings.ocr_language
        )

    def extract_text(self, pdf_path: str) -> str:
        """PDF → images → text"""
        try:
            # Convert PDF to images
            images = self.pdf_converter.convert(pdf_path, dpi=settings.ocr_dpi)
            logger.info(f"Converted PDF to {len(images)} images")

            # Extract text from images
            all_text = ""
            for i, image in enumerate(images):
                text = self.text_extractor.extract(image)
                all_text += text + "\n"
                logger.debug(f"Page {i+1}: {len(text)} characters")

            logger.info(f"Extracted {len(all_text)} characters from {pdf_path}")
            return all_text

        except Exception as e:
            raise OcrException(f"OCR failed for {pdf_path}: {e}")

# src/features/ocr/pdf_converter.py
from pdf2image import convert_from_path
from PIL import Image
import tempfile
from pathlib import Path

class PDFToImages:
    """Convert PDF pages to PIL Image objects"""

    def __init__(self, poppler_path: str = ''):
        self.poppler_path = poppler_path or None

    def convert(self, pdf_path: str, dpi: int = 300) -> list[Image.Image]:
        """PDF → list of PIL Images"""
        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                poppler_path=self.poppler_path
            )
            return images
        except Exception as e:
            raise ValueError(f"PDF conversion failed: {e}")

# src/features/ocr/text_extractor.py
import pytesseract
from PIL import Image

class ImageToText:
    """Extract text from images using Tesseract OCR"""

    def __init__(self, tesseract_path: str = 'tesseract', language: str = 'eng'):
        self.tesseract_path = tesseract_path
        self.language = language
        pytesseract.pytesseract.pytesseract_cmd = tesseract_path

    def extract(self, image: Image.Image) -> str:
        """Image → text using Tesseract"""
        try:
            text = pytesseract.image_to_string(image, lang=self.language)
            return text
        except Exception as e:
            raise ValueError(f"Text extraction failed: {e}")
```

### Day 5: Create Anonymization Feature (Plugin System)

**Plugin system for PII patterns:**

```python
# src/features/anonymization/__init__.py
from .redactor import Redactor
from .pii_patterns import registry, PIIPattern

__all__ = ['Redactor', 'registry', 'PIIPattern']

# src/features/anonymization/pii_patterns.py
from dataclasses import dataclass
from enum import Enum
import re

@dataclass
class PIIPattern:
    """PII pattern definition"""
    name: str
    regex: str
    replacement: str
    description: str = ""

class PIIPatternRegistry:
    """Registry for pluggable PII patterns"""

    def __init__(self):
        self.patterns = {}
        self._register_defaults()

    def _register_defaults(self):
        """Built-in PII patterns"""
        patterns = [
            PIIPattern(
                name="ssn",
                regex=r"\b\d{3}-\d{2}-\d{4}\b",
                replacement="[SSN REDACTED]",
                description="Social Security Numbers (XXX-XX-XXXX)"
            ),
            PIIPattern(
                name="mrn",
                regex=r"MRN[:\s]+([A-Z0-9]+)",
                replacement="[MRN REDACTED]",
                description="Medical Record Numbers"
            ),
            PIIPattern(
                name="phone",
                regex=r"(\+?1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
                replacement="[PHONE REDACTED]",
                description="Phone numbers (XXX-XXX-XXXX)"
            ),
            PIIPattern(
                name="email",
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                replacement="[EMAIL REDACTED]",
                description="Email addresses"
            ),
            # Add more patterns from current system
        ]
        for pattern in patterns:
            self.register(pattern)

    def register(self, pattern: PIIPattern):
        """Register a new pattern"""
        self.patterns[pattern.name] = pattern

    def get(self, name: str) -> PIIPattern:
        """Get pattern by name"""
        if name not in self.patterns:
            raise ValueError(f"Unknown pattern: {name}")
        return self.patterns[name]

    def list_patterns(self) -> list[str]:
        """List all registered patterns"""
        return list(self.patterns.keys())

# Global registry
registry = PIIPatternRegistry()

# src/features/anonymization/redactor.py
from src.core.logging import get_logger
from src.core.exceptions import AnonymizationException
import re

logger = get_logger(__name__)

class Redactor:
    """Redact PII from text using pattern registry"""

    def __init__(self, registry=None):
        if registry is None:
            from .pii_patterns import registry
        self.registry = registry

    def redact(self, text: str) -> str:
        """Apply all patterns to redact PII"""
        try:
            redacted = text
            for pattern_name, pattern in self.registry.patterns.items():
                # Count matches before redaction
                matches = re.findall(pattern.regex, text)
                if matches:
                    logger.debug(f"Found {len(matches)} matches for {pattern_name}")

                # Apply redaction
                redacted = re.sub(
                    pattern.regex,
                    pattern.replacement,
                    redacted,
                    flags=re.IGNORECASE
                )

            logger.info(f"Redacted text from {len(text)} → {len(redacted)} chars")
            return redacted

        except Exception as e:
            raise AnonymizationException(f"Redaction failed: {e}")

    def get_redaction_report(self, original: str, redacted: str) -> dict:
        """Report what was redacted"""
        report = {}
        for pattern_name, pattern in self.registry.patterns.items():
            matches = re.findall(pattern.regex, original)
            if matches:
                report[pattern_name] = len(matches)
        return report
```

### Days 6-7: Create Metadata Feature (Strategy Pattern)

**Extractors as pluggable strategies:**

```python
# src/features/metadata/__init__.py
from .extractor import MetadataExtractor
from .extractors.base import BaseExtractor

__all__ = ['MetadataExtractor', 'BaseExtractor']

# src/features/metadata/extractors/base.py
from abc import ABC, abstractmethod
from typing import Optional

class BaseExtractor(ABC):
    """Base class for metadata extractors"""

    @abstractmethod
    def extract(self, text: str) -> Optional[str]:
        """Extract value from text"""
        pass

    @abstractmethod
    def validate(self, value: str) -> bool:
        """Validate extracted value"""
        pass

    @property
    @abstractmethod
    def field_name(self) -> str:
        """Field name (e.g., 'gestational_age')"""
        pass

# src/features/metadata/extractors/gestational_age.py
from typing import Optional
import re
from .base import BaseExtractor

class GestationalAgeExtractor(BaseExtractor):
    """Extract gestational age from clinical text"""

    def extract(self, text: str) -> Optional[str]:
        """Find gestational age in format: ## weeks or ## w"""
        # Pattern: "28 weeks", "28w", "GA: 28"
        patterns = [
            r"(?:GA|gestational\s+age)[:\s]+(\d{1,2})\s+(?:weeks?|w)",
            r"(\d{1,2})\s+(?:weeks?|w)\s+(?:gestation|GA)",
            r"^(\d{1,2})\s+weeks?$"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

        return None

    def validate(self, value: str) -> bool:
        """GA must be 8-42 weeks"""
        try:
            weeks = int(value)
            return 8 <= weeks <= 42
        except (ValueError, TypeError):
            return False

    @property
    def field_name(self) -> str:
        return "gestational_age"

# src/features/metadata/extractor.py
from typing import Optional
from src.core.logging import get_logger
from src.core.exceptions import MetadataException
from .extractors.base import BaseExtractor
from .extractors.gestational_age import GestationalAgeExtractor
# Import more extractors as you create them

logger = get_logger(__name__)

class MetadataExtractor:
    """Coordinate all metadata extractors"""

    def __init__(self):
        self.extractors = [
            GestationalAgeExtractor(),
            # Add more extractors here
        ]

    def extract_all(self, text: str) -> dict:
        """Run all extractors and return results"""
        try:
            metadata = {}

            for extractor in self.extractors:
                try:
                    value = extractor.extract(text)

                    if value is not None:
                        if extractor.validate(value):
                            metadata[extractor.field_name] = value
                            logger.debug(f"Extracted {extractor.field_name}: {value}")
                        else:
                            logger.warning(f"Invalid value for {extractor.field_name}: {value}")
                    else:
                        logger.debug(f"No value found for {extractor.field_name}")

                except Exception as e:
                    logger.error(f"Error in {extractor.field_name} extractor: {e}")
                    continue

            logger.info(f"Extracted {len(metadata)} metadata fields")
            return metadata

        except Exception as e:
            raise MetadataException(f"Metadata extraction failed: {e}")
```

---

## Phase 3: Build Pipeline (Days 8-10)

### Goal

Create orchestration layer that coordinates all stages.

```python
# src/pipeline/__init__.py
from .orchestrator import ETLPipeline

__all__ = ['ETLPipeline']

# src/pipeline/context.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PipelineContext:
    """Shared state passed between pipeline stages"""
    pdf_path: str = ""
    extracted_text: str = ""
    anonymized_text: str = ""
    metadata: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

# src/pipeline/stages/__init__.py
from .ocr_stage import OCRStage
from .anonymization_stage import AnonymizationStage
from .extraction_stage import ExtractionStage
from .output_stage import OutputStage

__all__ = ['OCRStage', 'AnonymizationStage', 'ExtractionStage', 'OutputStage']

# src/pipeline/stages/base.py
from abc import ABC, abstractmethod
from ..context import PipelineContext

class BasePipelineStage(ABC):
    """Base class for pipeline stages"""

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute stage logic"""
        pass

# src/pipeline/stages/ocr_stage.py
from src.features.ocr import OCREngine
from src.core.logging import get_logger
from .base import BasePipelineStage

logger = get_logger(__name__)

class OCRStage(BasePipelineStage):
    """Stage 1: Extract text from PDF"""

    def __init__(self):
        self.engine = OCREngine()

    def execute(self, context: PipelineContext) -> PipelineContext:
        logger.info(f"OCR Stage: Processing {context.pdf_path}")
        context.extracted_text = self.engine.extract_text(context.pdf_path)
        return context

# src/pipeline/stages/anonymization_stage.py
from src.features.anonymization import Redactor, registry
from src.core.logging import get_logger
from .base import BasePipelineStage

logger = get_logger(__name__)

class AnonymizationStage(BasePipelineStage):
    """Stage 2: Redact PII"""

    def __init__(self):
        self.redactor = Redactor(registry=registry)

    def execute(self, context: PipelineContext) -> PipelineContext:
        logger.info("Anonymization Stage: Redacting PII")
        context.anonymized_text = self.redactor.redact(context.extracted_text)
        return context

# src/pipeline/stages/extraction_stage.py
from src.features.metadata import MetadataExtractor
from src.core.logging import get_logger
from .base import BasePipelineStage

logger = get_logger(__name__)

class ExtractionStage(BasePipelineStage):
    """Stage 3: Extract metadata"""

    def __init__(self):
        self.extractor = MetadataExtractor()

    def execute(self, context: PipelineContext) -> PipelineContext:
        logger.info("Extraction Stage: Extracting metadata")
        context.metadata = self.extractor.extract_all(context.anonymized_text)
        return context

# src/pipeline/stages/output_stage.py
from src.core.logging import get_logger
from .base import BasePipelineStage

logger = get_logger(__name__)

class OutputStage(BasePipelineStage):
    """Stage 4: Write outputs"""

    def execute(self, context: PipelineContext) -> PipelineContext:
        logger.info("Output Stage: Writing files")
        # Will be implemented in features/output
        return context

# src/pipeline/orchestrator.py
from pathlib import Path
from src.core.config import settings
from src.core.logging import get_logger
from .context import PipelineContext
from .stages import OCRStage, AnonymizationStage, ExtractionStage, OutputStage

logger = get_logger(__name__)

class ETLPipeline:
    """Main pipeline orchestrator"""

    def __init__(self):
        self.stages = [
            OCRStage(),
            AnonymizationStage(),
            ExtractionStage(),
            OutputStage(),
        ]

    def process_reports(self, pdf_paths: list[str]) -> list[dict]:
        """Process multiple reports"""
        logger.info(f"Starting pipeline for {len(pdf_paths)} reports")

        results = []
        for pdf_path in pdf_paths:
            try:
                result = self.process_single(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Pipeline failed for {pdf_path}: {e}")
                results.append({'success': False, 'error': str(e), 'pdf': pdf_path})

        logger.info(f"Pipeline complete. Success: {sum(1 for r in results if r.get('success'))}/{len(results)}")
        return results

    def process_single(self, pdf_path: str) -> dict:
        """Process single report through all stages"""
        logger.info(f"Processing: {pdf_path}")

        context = PipelineContext(pdf_path=pdf_path)

        # Execute stages in order
        for stage in self.stages:
            context = stage.execute(context)

        return {
            'success': True,
            'pdf': pdf_path,
            'metadata': context.metadata
        }
```

---

## Phase 4: Backward Compatibility (Days 11-12)

### Facade Pattern — Old API Still Works

**Keep v1.0.0 interface working:**

```python
# src/pdf_handler.py (FACADE - delegates to new code)
"""Backward compatibility layer for v1.0.0 API"""

from pathlib import Path
from src.features.ocr import OCREngine
from src.core.logging import get_logger

logger = get_logger(__name__)

# Create singleton instances
_ocr_engine = None

def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine

def extract_text(pdf_path: str) -> str:
    """v1.0.0 API - delegates to OCR feature"""
    logger.info(f"[DEPRECATED] extract_text() - use OCREngine directly")
    engine = _get_ocr_engine()
    return engine.extract_text(pdf_path)

def write_anonymized_pdf(text: str, output_path: str) -> None:
    """v1.0.0 API - delegates to output feature"""
    logger.info(f"[DEPRECATED] write_anonymized_pdf() - use PDFGenerator directly")
    # Will delegate to OutputStage
    from src.features.output import PDFGenerator
    gen = PDFGenerator()
    gen.generate(text, output_path)

# src/anonymizer.py (FACADE)
"""Backward compatibility for v1.0.0 API"""

from src.features.anonymization import Redactor, registry
from src.core.logging import get_logger

logger = get_logger(__name__)

_redactor = None

def _get_redactor():
    global _redactor
    if _redactor is None:
        _redactor = Redactor(registry=registry)
    return _redactor

def anonymize(text: str) -> str:
    """v1.0.0 API - delegates to redactor"""
    logger.info("[DEPRECATED] anonymize() - use Redactor directly")
    redactor = _get_redactor()
    return redactor.redact(text)

# src/extractor.py (FACADE)
"""Backward compatibility for v1.0.0 API"""

from src.features.metadata import MetadataExtractor
from src.core.logging import get_logger

logger = get_logger(__name__)

_extractor = None

def _get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = MetadataExtractor()
    return _extractor

def extract_metadata(text: str) -> dict:
    """v1.0.0 API - delegates to metadata feature"""
    logger.info("[DEPRECATED] extract_metadata() - use MetadataExtractor directly")
    extractor = _get_extractor()
    return extractor.extract_all(text)
```

---

## Phase 5-6: Testing + Deployment

See [DEVELOPMENT.md](DEVELOPMENT.md) for testing on Phase 5
See [DEPLOYMENT.md](DEPLOYMENT.md) for Phase 6 production setup

---

## Summary: What Changed?

| Aspect                   | v1.0.0                               | v2.0.0                                  |
| ------------------------ | ------------------------------------ | --------------------------------------- |
| **Adding PII pattern**   | Edit anonymizer.py (20 min + review) | `registry.register(pattern)` (5 min)    |
| **Testing anonymizer**   | Need full PDF setup (complex)        | Independent unit test (5 min)           |
| **Code organization**    | 4 files, unclear roles               | 25+ files, clear features               |
| **Adding new extractor** | Monolithic refactor                  | Implement interface + register (30 min) |
| **Error handling**       | Ad-hoc try/except                    | Consistent exception hierarchy          |
| **Configuration**        | Hardcoded in files                   | Environment variables + singleton       |
| **Logging**              | Print statements                     | Structured logs with levels             |
| **Testability**          | Cannot test OCR without PDF          | Test each stage independently           |

---

## Next: Handoff for Implementation

Ready to start coding?

1. **TODAY (4 hours):** Phase 0 hotfix
2. **Tomorrow (Days 1-3):** Create `src/core/`
3. **Wed-Thu (Days 4-7):** Create `src/features/`
4. **Fri-Sat (Days 8-10):** Create `src/pipeline/`

See [REFACTORING_CHECKLIST.md](../REFACTORING_CHECKLIST.md) to track progress.
