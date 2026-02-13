# Features Reference (v1.1.1)

**Complete documentation of implemented features.**

---

## Current Features

### 1. OCR Text Extraction

**What it does:** Extracts text from scanned PDF files using Tesseract OCR at 300 DPI.

**Implementation:** [src/features/ocr/engine.py](../src/features/ocr/engine.py)

```python
from src.core import Settings
from src.features.ocr import OCREngine, load_ocr_config

settings = Settings.load()
engine = OCREngine(load_ocr_config(settings))
text = engine.extract_text("path/to/report.pdf")
```

**Technical details:**

- Uses `pdf2image` to convert PDF pages to images
- Processes at 300 DPI for high accuracy
- Concatenates text from all pages
- Requires Tesseract OCR and Poppler installed

**Supported formats:**

- Single-page PDFs
- Multi-page PDFs (all pages processed)
- Scanned documents (image-based PDFs)

---

### 2. PII Anonymization (4 Patterns)

**What it does:** Redacts patient identifiers from extracted text using regex patterns.

**Implementation:** [src/features/anonymization](../src/features/anonymization)

```python
from src.features.anonymization import PIIRedactor, build_default_registry

registry = build_default_registry()
redactor = PIIRedactor(registry.get_all())
anonymized = redactor.redact(raw_text)
```

**Current patterns:**

| Field         | Pattern                                     | Replacement                   |
| ------------- | ------------------------------------------- | ----------------------------- |
| Patient Name  | `Patient Name[:\s]+[A-Za-z][A-Za-z\s]+`     | `Patient Name: [ANONYMIZED]`  |
| Patient ID    | `Patient ID[:\s]+[A-Za-z0-9][A-Za-z0-9_-]*` | `Patient ID: [ANONYMIZED]`    |
| Hospital Name | `Hospital Name[:\s]+[A-Za-z][A-Za-z\s]+`    | `Hospital Name: [ANONYMIZED]` |
| Clinician     | `Clinician[:\s]+[A-Za-z][A-Za-z\s]+`        | `Clinician: [ANONYMIZED]`     |

**Example:**

```
Input:  "Patient Name: John Doe, Patient ID: 12345"
Output: "Patient Name: [ANONYMIZED], Patient ID: [ANONYMIZED]"
```

**Adding patterns:** See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-pii-patterns)

---

### 3. Metadata Extraction (5 Fields)

**What it does:** Parses clinical information from anonymized report text.

**Implementation:** [src/features/metadata/extractor.py](../src/features/metadata/extractor.py)

```python
from src.features.metadata import (
  AgeExtractor,
  BMIExtractor,
  FindingsExtractor,
  GestationalAgeExtractor,
  MetadataExtractor,
)

extractor = MetadataExtractor(
  [GestationalAgeExtractor(), AgeExtractor(), BMIExtractor(), FindingsExtractor()]
)
metadata = extractor.extract_all(anonymized_text)
```

**Fields extracted:**

| Field             | Description       | Example                                |
| ----------------- | ----------------- | -------------------------------------- |
| `patient_id`      | UUID (generated)  | `550e8400-e29b-41d4-a716-446655440000` |
| `gestational_age` | Pregnancy weeks   | `"40 weeks"`                           |
| `age`             | Patient age       | `32`                                   |
| `BMI`             | Body mass index   | `28.5`                                 |
| `findings`        | Clinical findings | `["Normal", "No abnormalities"]`       |

**Output example:**

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "gestational_age": "40 weeks 3 days",
  "age": 32,
  "BMI": 28.5,
  "findings": ["Head: Normal biometry", "Brain: No abnormalities"]
}
```

**Compatibility note:** JSON output also includes aliases `demographic_age` and `examination_findings`.

---

### 4. Anonymized PDF Generation

**What it does:** Creates a new PDF with anonymized text content.

**Implementation:** [src/features/output/pdf_generator.py](../src/features/output/pdf_generator.py)

```python
from src.features.output import PDFGenerator

PDFGenerator().generate(
  anonymized_text="[ANONYMIZED] content...",
  output_path="output.pdf",
)
```

**Technical details:**

- Uses `fpdf` to generate new PDFs
- Preserves text content with anonymized values
- Sanitizes non-Latin characters
- Creates single-font, text-based output

---

### 5. JSON Metadata Export

**What it does:** Saves extracted metadata to structured JSON file.

**Implementation:** [src/features/output/json_serializer.py](../src/features/output/json_serializer.py)

```python
from src.features.output import JSONSerializer

JSONSerializer().serialize(metadata_list, "data/patient_metadata.json")
```

**Output schema:**

```json
{
  "dataResources": [
    {
      "patient_id": "550e8400-e29b-41d4-a716-446655440000",
      "gestational_age": "40 weeks",
      "age": 32,
      "demographic_age": 32,
      "BMI": 28.5,
      "findings": ["Finding 1", "Finding 2"],
      "examination_findings": ["Finding 1", "Finding 2"]
    }
  ]
}
```

---

### 6. UUID-Based De-identification

**What it does:** Maps original filenames to random UUIDs for privacy.

**Implementation:** [src/features/anonymization/uuid_service.py](../src/features/anonymization/uuid_service.py)

**How it works:**

1. Original filename: `patient_10785.pdf`
2. Generated UUID: `550e8400-e29b-41d4-a716-446655440000`
3. Output filename: `550e8400-e29b-41d4-a716-446655440000.pdf`
4. Mapping saved to: `data/id_map.json`

**Mapping file format:**

```json
{
  "patient_10785": "550e8400-e29b-41d4-a716-446655440000",
  "patient_10786": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

**Security:** The `id_map.json` file is excluded from git via `.gitignore`. Keep this file secure—it's the key to re-identifying patients.

---

### 7. Error Handling & Recovery

**What it does:** Continues processing when individual files fail, tracks results.

**Implementation:** [src/pipeline/orchestrator.py](../src/pipeline/orchestrator.py)

**Features (added in v1.1.0):**

- Per-file try-except blocks
- Success/failure tracking
- Processing summary with visual indicators
- Exit codes for CI/CD (0 = success, 1 = failures)
- Stack traces logged to stderr

**Example output:**

```
Processing: report_001.pdf
✅ Saved anonymized report to data/anonymized_reports/...
Processing: report_002.pdf
❌ Error processing report_002.pdf: OCR failed
Processing: report_003.pdf
✅ Saved anonymized report to data/anonymized_reports/...

=== PROCESSING SUMMARY ===
✅ Successfully processed: 2 reports
❌ Failed: 1 reports
  - report_002.pdf
```

---

## Feature Matrix

| Feature                        | Status         | Location                     |
| ------------------------------ | -------------- | ---------------------------- |
| OCR Text Extraction            | ✅ Implemented | `src/features/ocr`           |
| PII Anonymization (4 patterns) | ✅ Implemented | `src/features/anonymization` |
| Metadata Extraction (5 fields) | ✅ Implemented | `src/features/metadata`      |
| Anonymized PDF Generation      | ✅ Implemented | `src/features/output`        |
| JSON Metadata Export           | ✅ Implemented | `src/features/output`        |
| UUID De-identification         | ✅ Implemented | `src/features/anonymization` |
| Error Handling                 | ✅ Implemented | `src/pipeline`               |

---

## Planned Features

See [ROADMAP.md](ROADMAP.md) for planned improvements including:

- Additional PII patterns (SSN, DOB, phone, email, etc.)
- Environment-based configuration (no hardcoded paths)
- Test suite with 85%+ coverage
- Multiprocessing for batch speedup
- AES-256 encryption for sensitive files
- Docker containerization
- CI/CD pipeline

---

## Configuration

Configuration is managed via environment variables (see `.env.example`):

| Setting          | Location | Default                                        |
| ---------------- | -------- | ---------------------------------------------- |
| Poppler path     | `.env`   | `C:\poppler-24.08.0\Library\bin`               |
| Tesseract path   | `.env`   | `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| OCR DPI          | `.env`   | `300`                                          |
| Input directory  | `.env`   | `data/raw_reports`                             |
| Output directory | `.env`   | `data/anonymized_reports`                      |

**Note:** You can override any value with environment variables at runtime.

---

## Next Steps

- **Setup:** See [SETUP.md](SETUP.md)
- **Add features:** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Future plans:** See [ROADMAP.md](ROADMAP.md)

---

## Internal Implementation Details

For developers contributing to the codebase, a deep dive into the architecture, class hierarchy, and execution flow is available in:

👉 **[Feature Analysis](FEATURE_ANALYSIS.md)**

This document covers:
- Pipeline orchestration logic
- Detailed class responsibilities
- Data flow diagrams
- Known technical debts and improvement opportunities
