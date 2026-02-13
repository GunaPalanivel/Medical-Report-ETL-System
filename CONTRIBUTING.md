# Contributing to Medical Report ETL System

Thank you for your interest in contributing! This guide covers everything you need to know to contribute effectively.

---

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Adding PII Patterns](#adding-pii-patterns)
- [Adding Metadata Fields](#adding-metadata-fields)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Tesseract OCR installed ([installation guide](docs/SETUP.md#tesseract-installation))
- Poppler for PDF processing ([installation guide](docs/SETUP.md#poppler-installation))
- Git for version control

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/Medical-Report-ETL-System.git
cd Medical-Report-ETL-System

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment settings
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Update POPPLER_PATH and TESSERACT_PATH in .env

# 5. Verify setup
python main.py
```

---

## How to Contribute

### Types of Contributions

| Type               | Description                   | Difficulty      |
| ------------------ | ----------------------------- | --------------- |
| **Bug Fix**        | Fix issues in existing code   | Easy            |
| **Documentation**  | Improve docs, fix typos       | Easy            |
| **PII Pattern**    | Add new anonymization pattern | Easy (5 min)    |
| **Metadata Field** | Add new field extraction      | Medium (15 min) |
| **New Feature**    | Add new capability            | Medium-Hard     |

### Finding Issues

- Look for issues labeled [`good first issue`](https://github.com/GunaPalanivel/Medical-Report-ETL-System/labels/good%20first%20issue)
- Check [`help wanted`](https://github.com/GunaPalanivel/Medical-Report-ETL-System/labels/help%20wanted) for more challenging tasks
- Review [docs/ROADMAP.md](docs/ROADMAP.md) for planned improvements

---

## Adding PII Patterns

The easiest way to contribute! Add a new regex pattern to redact additional PHI.

### Step 1: Edit the PII registry

Open `src/features/anonymization/pii_patterns.py` and add your pattern:

```python
registry = PIIPatternRegistry()
registry.register(
    PIIPattern(
        name="patient_name",
        regex=r"Patient Name[:\s]+[A-Za-z][A-Za-z\s]+",
        replacement="Patient Name: [ANONYMIZED]",
        priority=10,
    )
)

# ADD YOUR NEW PATTERN HERE
registry.register(
    PIIPattern(
        name="phone",
        regex=r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        replacement="[PHONE REDACTED]",
        priority=50,
    )
)
```

### Step 2: Test Your Pattern

```python
# Quick test
from src.features.anonymization import PIIRedactor, build_default_registry

registry = build_default_registry()
redactor = PIIRedactor(registry.get_all())
test_text = "Call 555-123-4567 for results"
result = redactor.redact(test_text)
print(result)  # Should show: "Call [PHONE REDACTED] for results"
```

### Step 3: Submit PR

```bash
git checkout -b feature/add-phone-pattern
git add src/features/anonymization/pii_patterns.py
git commit -m "feat(anonymization): add phone number PII pattern"
git push origin feature/add-phone-pattern
```

### Common PII Patterns to Add

| PHI Type | Suggested Regex                                               | Note                  |
| -------- | ------------------------------------------------------------- | --------------------- |
| Phone    | `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`                               | US format             |
| SSN      | `\b\d{3}-\d{2}-\d{4}\b`                                       | XXX-XX-XXXX           |
| Email    | `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z\|a-z]{2,}\b`        | Standard email        |
| DOB      | `\b(DOB\|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b` | Various formats       |
| MRN      | `\b(MRN\|Medical Record)[:\s]*\w+\b`                          | Medical Record Number |

---

## Adding Metadata Fields

Add extraction for a new clinical field from report text.

### Step 1: Add a new extractor

Create a new extractor in `src/features/metadata/extractors/`:

```python
from src.features.metadata.extractors.base import BaseExtractor


class BloodPressureExtractor(BaseExtractor):
    @property
    def field_name(self) -> str:
        return "blood_pressure"

    def extract(self, text: str):
        match = re.search(r"BP[:\s]*(\d{2,3})/(\d{2,3})", text)
        if match:
            return {
                "systolic": int(match.group(1)),
                "diastolic": int(match.group(2)),
            }
        return None

    def validate(self, value: object) -> bool:
        return isinstance(value, dict)
```

### Step 2: Register the extractor

Add the extractor in `src/features/metadata/extractor.py` where the list is built.

### Step 3: Test and Submit

```bash
python main.py  # Verify it extracts correctly
git checkout -b feature/add-blood-pressure-field
git add src/features/metadata/extractors/blood_pressure.py src/features/metadata/extractor.py
git commit -m "feat(metadata): add blood pressure extractor"
git push origin feature/add-blood-pressure-field
```

---

## Development Workflow

### Branch Naming

```
feature/    - New features (feature/add-email-pattern)
fix/        - Bug fixes (fix/ocr-crash-on-empty-pdf)
docs/       - Documentation (docs/update-setup-guide)
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Examples:**

```bash
feat(anonymizer): add SSN PII pattern
fix(extractor): handle missing gestational age gracefully
docs(readme): add troubleshooting section
```

### Running the Pipeline

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run main pipeline
python main.py

# Quick import test
python -c "from src import *; print('Imports OK')"
```

---

## Pull Request Process

### Before Submitting

1. Code runs without errors: `python main.py`
2. Imports work: `python -c "from src import *"`
3. Documentation updated (if applicable)
4. Commit messages follow convention

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature (PII pattern, metadata field, etc.)
- [ ] Documentation

## Testing

Describe how you tested the changes.

## Checklist

- [ ] Code runs without errors
- [ ] Updated relevant documentation
```

### Review Process

1. Submit PR against `main` branch
2. Maintainer reviews code
3. Address feedback (if any)
4. Maintainer merges PR

---

## Style Guide

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Add docstrings to functions

### Docstrings

```python
def extract_metadata(text):
    """
    Extract structured metadata from anonymized report text.

    Args:
        text: Anonymized report text string

    Returns:
        Dictionary containing extracted metadata fields
    """
```

### Project Structure

```
src/
├── __init__.py      # Package exports (update when adding public functions)
├── core/            # Settings, logging, exceptions, utils
├── features/        # OCR, anonymization, metadata, output
├── pipeline/        # Stage orchestration
├── pdf_handler.py   # Backward-compatible facade
├── anonymizer.py    # Backward-compatible facade
├── extractor.py     # Backward-compatible facade
└── json_writer.py   # Backward-compatible facade
```

---

## Questions?

- Open a [GitHub Issue](https://github.com/GunaPalanivel/Medical-Report-ETL-System/issues)
- Review existing [documentation](docs/)

Thank you for contributing!
