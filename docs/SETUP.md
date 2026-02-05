# Setup Guide

**Get the Medical Report ETL System running in 10 minutes.**

---

## Prerequisites

### System Requirements

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11)
- **Tesseract OCR** (language data + executables)
- **Poppler** (PDF processing utilities)
- **Git** (for version control)

### Platform-Specific Installation

#### Windows

```powershell
# 1. Install Tesseract (via executable installer)
# Download: https://github.com/UB-Mannheim/tesseract/wiki
# Run installer, note installation path (e.g., C:\Program Files\Tesseract-OCR)

# 2. Install Poppler
# Download: https://github.com/oschwartz10612/poppler-windows/releases/
# Extract to a folder (e.g., C:\poppler-24.08.0)

# 3. Verify installations
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
Test-Path "C:\poppler-24.08.0\Library\bin\pdftoppm.exe"
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
tesseract --version
pdftoppm -h
```

#### macOS

```bash
brew install tesseract poppler
tesseract --version
pdftoppm -h
```

---

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/GunaPalanivel/Medical-Report-ETL-System.git
cd Medical-Report-ETL-System
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages installed:**

- pytesseract
- pdf2image
- fpdf2
- Pillow

### Step 4: Configure System Paths

> **Important:** You must edit the paths in `src/pdf_handler.py` to match your system.

Open `src/pdf_handler.py` and update these lines:

```python
# Windows example:
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Linux example:
POPPLER_PATH = "/usr/bin"
# pytesseract will auto-detect if tesseract is in PATH
```

### Step 5: Verify Installation

```bash
# Test imports
python -c "from src import *; print('All imports OK')"

# Test Tesseract
python -c "import pytesseract; print('Tesseract OK')"

# Test PDF processing
python -c "from pdf2image import convert_from_path; print('PDF2Image OK')"
```

---

## Running the Pipeline

### 1. Prepare Input PDFs

Place scanned PDF files in `data/raw_reports/`:

```bash
# Check the input folder
ls data/raw_reports/
```

### 2. Run Pipeline

```bash
python main.py
```

**Expected output:**

```
Processing: report_001.pdf
✅ Saved anonymized report to data/anonymized_reports/550e8400-e29b-41d4-a716-446655440000.pdf
Processing: report_002.pdf
✅ Saved anonymized report to data/anonymized_reports/6ba7b810-9dad-11d1-80b4-00c04fd430c8.pdf
...
✅ Saved metadata to data/patient_metadata.json

=== PROCESSING SUMMARY ===
✅ Successfully processed: 50 reports
❌ Failed: 0 reports
```

### 3. Check Outputs

```bash
# Anonymized PDFs (with UUID filenames)
ls data/anonymized_reports/

# Structured metadata
cat data/patient_metadata.json

# UUID mapping (keep this secure!)
cat data/id_map.json
```

---

## Project Structure

```
Medical-Report-ETL-System/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── src/
│   ├── __init__.py             # Package exports
│   ├── pdf_handler.py          # OCR + PDF generation (EDIT PATHS HERE)
│   ├── anonymizer.py           # PII redaction
│   ├── extractor.py            # Metadata extraction
│   └── json_writer.py          # JSON output
├── data/
│   ├── raw_reports/            # Input: your PDFs go here
│   ├── anonymized_reports/     # Output: redacted PDFs
│   ├── patient_metadata.json   # Output: extracted data
│   └── id_map.json             # Output: UUID mapping (sensitive!)
└── docs/                       # Documentation
```

---

## Troubleshooting

### "tesseract not found"

**Cause:** Tesseract path not configured correctly.

**Solution:** Edit `src/pdf_handler.py`:

```python
# Update to your actual path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Verify:**

```bash
python -c "import pytesseract; pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'; print(pytesseract.get_tesseract_version())"
```

### "poppler not found" or "Unable to get page count"

**Cause:** Poppler path not configured.

**Solution:** Edit `src/pdf_handler.py`:

```python
# Update to your actual path
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
```

**Verify:**

```bash
python -c "from pdf2image import convert_from_path; print(convert_from_path('test.pdf', poppler_path=r'C:\\poppler-24.08.0\\Library\\bin'))"
```

### "ModuleNotFoundError: No module named 'pytesseract'"

**Cause:** Dependencies not installed.

**Solution:**

```bash
pip install -r requirements.txt
pip list | grep -i tesseract
```

### Empty OCR output

**Cause:** Low quality scan or wrong DPI.

**Solution:** The system uses 300 DPI by default. For better results:

- Ensure source PDFs are 300+ DPI
- Check that text is clearly visible in the scanned images

### Import errors from src package

**Cause:** Running from wrong directory.

**Solution:** Always run from project root:

```bash
cd Medical-Report-ETL-System
python main.py
```

---

## Data Flow

```
data/raw_reports/*.pdf
        │
        ▼
┌──────────────────────┐
│  read_pdf_text()     │  OCR at 300 DPI
│  (pdf_handler.py)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  anonymize_text()    │  4 PII patterns replaced
│  (anonymizer.py)     │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌───────────────┐
│write_   │  │extract_       │
│anonymized│ │metadata()     │
│_pdf()   │  │(extractor.py) │
└────┬────┘  └───────┬───────┘
     │               │
     ▼               ▼
data/anonymized_    patient_metadata.json
reports/*.pdf       + id_map.json
```

---

## Next Steps

- **Setup complete?** Run `python main.py` with your PDFs
- **Want to add PII patterns?** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Understand the features?** See [FEATURES.md](FEATURES.md)
- **Future plans?** See [ROADMAP.md](ROADMAP.md)
