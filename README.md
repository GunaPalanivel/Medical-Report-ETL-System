# Medical Report ETL System

**Extract text from scanned medical reports, anonymize PII, and output structured data.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.1-green.svg)](CHANGELOG.md)

---

## Overview

A Python ETL pipeline that processes scanned medical PDF reports and produces:

- **Anonymized PDFs** — Patient identifiers replaced with `[ANONYMIZED]` placeholders
- **Structured JSON** — Extracted metadata (gestational age, demographics, clinical findings)
- **UUID Mapping** — Original-to-anonymized ID mapping for authorized data linkage

Designed for healthcare research scenarios where raw reports contain PHI that must be redacted before analysis.

---

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Tesseract OCR** — [Installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- **Poppler** — [Windows](https://github.com/oschwartz10612/poppler-windows/releases) | [macOS](https://formulae.brew.sh/formula/poppler) | [Linux](https://poppler.freedesktop.org/)

### Installation

```bash
git clone https://github.com/GunaPalanivel/Medical-Report-ETL-System.git
cd Medical-Report-ETL-System

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Configuration

Edit paths in [src/pdf_handler.py](src/pdf_handler.py) to match your system:

```python
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"  # Update this
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this
```

### Usage

1. Place PDF files in `data/raw_reports/`
2. Run the pipeline:

```bash
python main.py
```

3. Outputs appear in:
   - `data/anonymized_reports/` — Redacted PDFs
   - `data/patient_metadata.json` — Extracted structured data
   - `data/id_map.json` — UUID mapping (keep secure!)

---

## Features

### PII Anonymization (4 Patterns)

| Field         | Regex Pattern                | Replacement    |
| ------------- | ---------------------------- | -------------- |
| Patient Name  | `Patient Name[:\s]+[\w\s]+`  | `[ANONYMIZED]` |
| Patient ID    | `Patient ID[:\s]+\w+`        | `[ANONYMIZED]` |
| Hospital Name | `Hospital Name[:\s]+[\w\s]+` | `[ANONYMIZED]` |
| Clinician     | `Clinician[:\s]+[\w\s]+`     | `[ANONYMIZED]` |

### Metadata Extraction (5 Fields)

- `patient_id` — UUID (anonymized identifier)
- `gestational_age` — Extracted from report text
- `demographic_age` — Patient age
- `BMI` — Body mass index
- `examination_findings` — Clinical findings array

### Processing Pipeline

```
raw_reports/*.pdf
       │
       ▼
┌─────────────────┐
│  OCR (Tesseract)│  read_pdf_text() @ 300 DPI
└────────┬────────┘
         │ raw text
         ▼
┌─────────────────┐
│   Anonymize     │  anonymize_text() - 4 PII patterns
└────────┬────────┘
         │ redacted text
         ▼
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Write  │ │Extract│  write_anonymized_pdf() / extract_metadata()
│PDF    │ │Fields │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
anonymized_   patient_
reports/      metadata.json
```

---

## Project Structure

```
Medical-Report-ETL-System/
├── main.py                 # Entry point - orchestrates pipeline
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py         # Package exports
│   ├── pdf_handler.py      # OCR text extraction + PDF writing
│   ├── anonymizer.py       # PII redaction (4 patterns)
│   ├── extractor.py        # Metadata field extraction
│   └── json_writer.py      # JSON output formatting
├── data/
│   ├── raw_reports/        # Input: scanned PDFs
│   ├── anonymized_reports/ # Output: redacted PDFs
│   ├── patient_metadata.json
│   └── id_map.json         # UUID mapping (sensitive!)
└── docs/                   # Documentation
```

---

## Current Limitations

> **Note:** This is v1.1.1 — a working baseline with known limitations.

| Limitation            | Impact                                     | Planned Fix                |
| --------------------- | ------------------------------------------ | -------------------------- |
| Hardcoded paths       | Must edit `pdf_handler.py` for each system | Environment variables      |
| 4 PII patterns only   | May miss some PHI (SSN, DOB, phone, etc.)  | Expand to 8+ patterns      |
| No tests              | Cannot verify changes safely               | Add pytest suite           |
| Sequential processing | Slow for large batches                     | Multiprocessing            |
| No encryption         | `id_map.json` stored in plaintext          | AES-256 at-rest encryption |

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned improvements.

---

## Documentation

- [SETUP.md](docs/SETUP.md) — Detailed installation instructions
- [FEATURES.md](docs/FEATURES.md) — Complete feature documentation
- [HIPAA_COMPLIANCE.md](docs/HIPAA_COMPLIANCE.md) — Privacy considerations
- [ROADMAP.md](docs/ROADMAP.md) — Future development plans
- [CHANGELOG.md](CHANGELOG.md) — Version history

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick contributions:**

- Add a PII pattern to `src/anonymizer.py`
- Add a metadata field to `src/extractor.py`
- Report issues via [GitHub Issues](https://github.com/GunaPalanivel/Medical-Report-ETL-System/issues)

---

## Security

- **Never commit** `data/id_map.json` — contains the UUID↔original mapping
- Report vulnerabilities via [SECURITY.md](SECURITY.md)
- See [HIPAA_COMPLIANCE.md](docs/HIPAA_COMPLIANCE.md) for privacy guidance

---

## License

[MIT License](LICENSE) — Free for use in healthcare organizations.

---

## Acknowledgments

Built for healthcare data sharing scenarios where privacy is critical. Inspired by real-world challenges in clinical research data anonymization.
