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

# 4. Configure paths in src/pdf_handler.py for your system
# Edit POPPLER_PATH and tesseract_cmd

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

### Step 1: Edit anonymizer.py

Open `src/anonymizer.py` and add your pattern:

```python
def anonymize_text(text):
    """Anonymize PII fields in extracted text."""
    # Existing patterns
    text = re.sub(r"Patient Name[:\s]+[\w\s]+", "Patient Name: [ANONYMIZED]", text)
    text = re.sub(r"Patient ID[:\s]+\w+", "Patient ID: [ANONYMIZED]", text)
    text = re.sub(r"Hospital Name[:\s]+[\w\s]+", "Hospital Name: [ANONYMIZED]", text)
    text = re.sub(r"Clinician[:\s]+[\w\s]+", "Clinician: [ANONYMIZED]", text)

    # ADD YOUR NEW PATTERN HERE
    # Example: Redact phone numbers
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE REDACTED]", text)

    return text
```

### Step 2: Test Your Pattern

```python
# Quick test
from src.anonymizer import anonymize_text

test_text = "Call 555-123-4567 for results"
result = anonymize_text(test_text)
print(result)  # Should show: "Call [PHONE REDACTED] for results"
```

### Step 3: Submit PR

```bash
git checkout -b feature/add-phone-pattern
git add src/anonymizer.py
git commit -m "feat(anonymizer): add phone number PII pattern"
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

### Step 1: Edit extractor.py

Open `src/extractor.py` and add your extraction logic:

```python
def extract_metadata(text):
    """Extract structured metadata from anonymized text."""
    metadata = {}

    # Existing extractions...

    # ADD YOUR NEW FIELD HERE
    # Example: Extract blood pressure
    bp_match = re.search(r"BP[:\s]*(\d{2,3})/(\d{2,3})", text)
    if bp_match:
        metadata["blood_pressure"] = {
            "systolic": int(bp_match.group(1)),
            "diastolic": int(bp_match.group(2))
        }

    return metadata
```

### Step 2: Update JSON Writer (Optional)

If the field needs special formatting, update `src/json_writer.py`:

```python
def save_metadata_json(metadata_list, output_path):
    # Add your field to the output schema
    formatted["dataResources"].append({
        # existing fields...
        "blood_pressure": entry.get("blood_pressure"),
    })
```

### Step 3: Test and Submit

```bash
python main.py  # Verify it extracts correctly
git checkout -b feature/add-blood-pressure-field
git add src/extractor.py src/json_writer.py
git commit -m "feat(extractor): add blood pressure metadata extraction"
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
├── pdf_handler.py   # OCR + PDF writing
├── anonymizer.py    # PII redaction patterns
├── extractor.py     # Metadata field extraction
└── json_writer.py   # JSON output formatting
```

---

## Questions?

- Open a [GitHub Issue](https://github.com/GunaPalanivel/Medical-Report-ETL-System/issues)
- Review existing [documentation](docs/)

Thank you for contributing!
