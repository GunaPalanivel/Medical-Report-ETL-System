# Development Guide

**Build features, run tests, format code, and contribute.**

---

## Development Workflow

### 1. Create Feature Branch

```bash
# Create feature branch
git checkout -b feature/add-new-pii-pattern
# or
git checkout -b fix/reduce-false-positives
# or
git checkout -b docs/improve-setup-guide
```

### 2. Make Code Changes

```bash
# Edit files in src/ or tests/
nano src/features/anonymization/pii_patterns.py
# or use your editor
```

### 3. Run Tests Locally

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/features/test_anonymization.py -v

# Specific test
pytest tests/features/test_anonymization.py::test_redact_names -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

### 4. Format & Lint Code

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### 5. Commit & Push

```bash
# Stage changes
git add src/features/anonymization/pii_patterns.py tests/features/test_anonymization.py

# Commit with descriptive message
git commit -m "feat: add SSN PII pattern with tests"

# Push to your fork
git push origin feature/add-new-pii-pattern
```

### 6. Open Pull Request

- Go to GitHub
- Click "New Pull Request"
- Describe what you changed and why
- Ensure GitHub Actions pass (tests + lint)
- Wait for review

---

## Common Development Tasks

### Adding a PII Pattern (5 minutes)

**Goal:** Detect and redact a new type of sensitive information.

#### Step 1: Define Pattern

```python
# src/features/anonymization/pii_patterns.py
from dataclasses import dataclass
import re

@dataclass
class PIIPattern:
    name: str
    regex: str
    replacement: str

# Add to registry
PATTERNS = [
    PIIPattern(
        name="ssn",
        regex=r"\b\d{3}-\d{2}-\d{4}\b",
        replacement="[SSN REDACTED]"
    ),
    # NEW: Add your pattern here
    PIIPattern(
        name="phone_us",
        regex=r"(\+?1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
        replacement="[PHONE REDACTED]"
    ),
]

class PIIPatternRegistry:
    def __init__(self):
        self.patterns = {p.name: p for p in PATTERNS}

    def register(self, pattern: PIIPattern):
        """Register new pattern at runtime"""
        self.patterns[pattern.name] = pattern

registry = PIIPatternRegistry()
```

#### Step 2: Write Test

```python
# tests/features/test_anonymization.py
import pytest
from src.features.anonymization.pii_patterns import registry, PIIPattern

def test_redact_phone_us():
    """Test US phone number redaction"""
    text = "Call me at (555) 123-4567 for details"
    # After redaction:
    # "Call me at [PHONE REDACTED] for details"
    assert "[PHONE REDACTED]" in redacted_text
    assert "555" not in redacted_text

def test_redact_phone_international():
    """Test international phone redaction"""
    text = "Contact +1-800-555-1234"
    # Should redact with country code
    assert "[PHONE REDACTED]" in redacted_text
```

#### Step 3: Run Tests

```bash
pytest tests/features/test_anonymization.py::test_redact_phone_us -v
```

#### Step 4: Commit

```bash
git add src/features/anonymization/pii_patterns.py tests/features/test_anonymization.py
git commit -m "feat: add US phone PII pattern with tests"
```

✅ **Done!** No need to edit redactor.py.

---

### Adding a Metadata Extractor (30 minutes)

**Goal:** Extract a new clinical field from medical text.

#### Step 1: Create Extractor Class

```python
# src/features/metadata/extractors/blood_pressure.py
from abc import ABC, abstractmethod
import re
from typing import Optional

class BaseExtractor(ABC):
    """All extractors inherit from this"""

    @abstractmethod
    def extract(self, text: str) -> Optional[str]:
        """Extract field from text. Return None if not found."""
        pass

    @abstractmethod
    def validate(self, value: str) -> bool:
        """Validate extracted value. Return True if valid."""
        pass

    @property
    @abstractmethod
    def field_name(self) -> str:
        """Return field name for JSON output"""
        pass

class BloodPressureExtractor(BaseExtractor):
    """Extract blood pressure readings like 120/80"""

    def extract(self, text: str) -> Optional[str]:
        # Match patterns like "BP: 120/80" or "BP 120/80"
        match = re.search(
            r"BP\s*[:=]?\s*(\d{2,3})\s*[/\\]\s*(\d{2,3})",
            text,
            re.IGNORECASE
        )
        return f"{match.group(1)}/{match.group(2)}" if match else None

    def validate(self, value: str) -> bool:
        """BP should be reasonable: systolic 80-220, diastolic 40-130"""
        try:
            systolic, diastolic = map(int, value.split('/'))
            return 80 <= systolic <= 220 and 40 <= diastolic <= 130
        except:
            return False

    @property
    def field_name(self) -> str:
        return "blood_pressure"
```

#### Step 2: Register Extractor

```python
# src/features/metadata/extractor.py
from src.features.metadata.extractors.blood_pressure import BloodPressureExtractor

class MetadataExtractor:
    def __init__(self):
        self.extractors = [
            GestationalAgeExtractor(),
            DemographicsExtractor(),
            FindingsExtractor(),
            BloodPressureExtractor(),  # ← Add here
        ]

    def extract_all(self, text: str) -> dict:
        metadata = {}
        for extractor in self.extractors:
            value = extractor.extract(text)
            if value and extractor.validate(value):
                metadata[extractor.field_name] = value
        return metadata
```

#### Step 3: Write Tests

```python
# tests/features/test_metadata.py
from src.features.metadata.extractors.blood_pressure import BloodPressureExtractor

def test_extract_blood_pressure_common_format():
    extractor = BloodPressureExtractor()
    text = "Patient BP: 120/80 mmHg"
    assert extractor.extract(text) == "120/80"
    assert extractor.validate("120/80") is True

def test_extract_blood_pressure_invalid_value():
    extractor = BloodPressureExtractor()
    assert extractor.validate("50/30") is False  # Too low
    assert extractor.validate("250/150") is False  # Too high

def test_extract_blood_pressure_not_found():
    extractor = BloodPressureExtractor()
    text = "No vital signs recorded"
    assert extractor.extract(text) is None

def test_blood_pressure_field_name():
    extractor = BloodPressureExtractor()
    assert extractor.field_name == "blood_pressure"
```

#### Step 4: Run Tests

```bash
pytest tests/features/test_metadata.py::test_extract_blood_pressure_common_format -v
```

#### Step 5: Commit

```bash
git add src/features/metadata/extractors/blood_pressure.py \
        tests/features/test_metadata.py \
        src/features/metadata/extractor.py
git commit -m "feat: add blood pressure metadata extractor with tests"
```

✅ **Done!** Extractor is automatically used in pipeline.

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run by Category

```bash
# Core layer tests
pytest tests/core/ -v

# Feature tests only
pytest tests/features/ -v

# Integration tests only
pytest tests/integration/ -v

# Performance benchmarks
pytest tests/benchmarks/ -v --benchmark-compare
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ -v --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test

```bash
# By test file
pytest tests/features/test_anonymization.py -v

# By test function
pytest tests/features/test_anonymization.py::test_redact_names -v

# By pattern
pytest -k "redact" -v  # Run all tests with "redact" in name
```

---

## Code Quality

### Format Code

```bash
# Format all Python files
black src/ tests/ docs/

# Format specific file
black src/features/ocr/engine.py
```

### Check Linting

```bash
# Check linting issues
flake8 src/ tests/

# Show detailed errors
flake8 src/features/anonymization/ --show-source --statistics
```

### Type Checking

```bash
# Check type hints
mypy src/

# Strict mode
mypy src/ --strict
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Run hooks on staged files (automatic on git commit)
git commit -m "feat: add new feature"
```

---

## Testing Best Practices

### 1. Module-Level Tests

Test individual functions:

```python
# tests/features/test_ocr.py
from src.features.ocr.text_extractor import extract_text

def test_extract_text_from_image():
    """Test text extraction from sample image"""
    image = Image.open("tests/fixtures/sample_page.png")
    text = extract_text(image)
    assert "Patient:" in text
    assert len(text) > 100
```

### 2. Feature-Level Tests

Test complete feature:

```python
# tests/features/test_anonymization.py
from src.features.anonymization.redactor import Redactor

def test_redact_all_pii():
    """Test that redactor removes all 8 PII types"""
    text = "John Doe, SSN 123-45-6789, DOB 01/01/1980, Phone: (555) 123-4567"
    redactor = Redactor()
    result = redactor.redact(text)

    # Check nothing identifiable remains
    assert "John" not in result
    assert "123-45-6789" not in result
    assert "555" not in result
```

### 3. Integration Tests

Test full pipeline:

```python
# tests/integration/test_end_to_end.py
from src.pipeline.orchestrator import ETLPipeline

def test_pipeline_processes_pdf_to_json():
    """Test end-to-end: PDF → anonymized PDF + JSON"""
    pipeline = ETLPipeline()
    result = pipeline.process_reports(["tests/fixtures/sample_report.pdf"])

    assert result["succeeded"] == 1
    assert result["failed"] == 0
    assert Path("data/anonymized_reports").exists()
    assert Path("data/patient_metadata.json").exists()
```

---

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Test additions
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `chore:` Maintenance

**Examples:**

```bash
git commit -m "feat(anonymization): add SSN PII pattern

- Add regex pattern for US SSN (XXX-XX-XXXX)
- Add validation for redaction
- Add 3 test cases

Closes #42"
```

```bash
git commit -m "fix(ocr): handle empty PDF pages gracefully"
```

---

## Common Issues

### Test Fails: "ModuleNotFoundError"

```bash
# Add src/ to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/

# Or use pytest in source directory
cd /path/to/project
pytest tests/
```

### Black Wants to Reformat My Code

Just let it:

```bash
black src/
git add src/
git commit -m "style: format code with black"
```

### Flake8 Complains About Long Lines

```python
# Before: Line too long (>88 chars)
result = redactor.redact(text) if text else None

# After: Line continuation
result = (
    redactor.redact(text)
    if text
    else None
)
```

---

## Next Steps

- ✅ Tests passing? Create Pull Request!
- 📚 Need architecture help? See [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)
- 🚀 Ready to deploy? See [DEPLOYMENT.md](DEPLOYMENT.md)
