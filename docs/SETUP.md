# Setup Guide

**Get the Medical Report ETL System running in 10 minutes.**

---

## Prerequisites

### System Requirements

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11)
- **Tesseract OCR** (language data + executables)
- **Poppler** (PDF processing utilities)
- **Git** (for version control)
- **4 GB RAM** minimum (8 GB recommended for batch processing)

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
C:\Program Files\Tesseract-OCR\tesseract.exe --version
dir C:\poppler-24.08.0\Library\bin\pdftoppm.exe
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

**Expected output:**

```
Successfully installed pytesseract pdf2image fpdf2 Pillow cryptography jsonschema pytest pytest-cov black flake8 mypy
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your system paths
# Windows example:
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler-24.08.0\Library\bin
INPUT_DIR=data/raw_reports
OUTPUT_DIR=data/anonymized_reports
METADATA_OUTPUT=data/patient_metadata.json
ID_MAP_PATH=data/id_map.json
LOG_DIR=logs
ENV=development
LOG_LEVEL=INFO

# Linux example:
TESSERACT_PATH=/usr/bin/tesseract
POPPLER_PATH=/usr/bin
INPUT_DIR=data/raw_reports
OUTPUT_DIR=data/anonymized_reports
METADATA_OUTPUT=data/patient_metadata.json
ID_MAP_PATH=data/id_map.json
LOG_DIR=logs
ENV=development
LOG_LEVEL=INFO
```

### Step 5: Verify Installation

```bash
# Test Tesseract integration
python -c "import pytesseract; print(pytesseract.pytesseract.get_tesseract_version())"

# Test PDF processing
python -c "from pdf2image import convert_from_path; print('PDF2Image OK')"

# Run basic sanity check
python -m pytest tests/ -v --collect-only | head -20
```

---

## Quick Test

### 1. Prepare Sample PDF

```bash
mkdir -p data/raw_reports
# Copy a sample PDF to data/raw_reports/
# Or use the included test PDF
```

### 2. Run Pipeline

```bash
python main.py
```

**Expected output:**

```
2026-02-05 10:30:45 - INFO - MEDICAL REPORT ETL PIPELINE STARTED
2026-02-05 10:30:45 - INFO - Found 1 PDF files to process
2026-02-05 10:30:47 - INFO - [1/1] Processing: sample_report.pdf
2026-02-05 10:30:52 - INFO - ✓ Successfully processed sample_report.pdf
2026-02-05 10:30:52 - INFO - PIPELINE COMPLETED: 1 succeeded, 0 failed
```

### 3. Check Outputs

```bash
# Anonymized PDF (with UUID filename)
ls -la data/anonymized_reports/
# Output: 550e8400-e29b-41d4-a716-446655440000.pdf

# Structured metadata
cat data/patient_metadata.json
# Output: {"dataResources": [...]}

# Processing logs
tail -20 logs/etl.log
```

---

## Configuration Reference

### Environment Variables

| Variable          | Purpose                       | Default                      | Example                                        |
| ----------------- | ----------------------------- | ---------------------------- | ---------------------------------------------- |
| `TESSERACT_PATH`  | Path to tesseract executable  | Auto-detected                | `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| `POPPLER_PATH`    | Path to poppler bin directory | Auto-detected                | `C:\poppler-24.08.0\Library\bin`               |
| `INPUT_DIR`       | Raw PDF input folder          | `data/raw_reports`           | Custom path allowed                            |
| `OUTPUT_DIR`      | Anonymized PDF output folder  | `data/anonymized_reports`    | Custom path allowed                            |
| `METADATA_OUTPUT` | JSON metadata file path       | `data/patient_metadata.json` | Custom filename allowed                        |
| `ID_MAP_PATH`     | UUID mapping file (protect!)  | `data/id_map.json`           | Custom path (add to .gitignore)                |
| `LOG_DIR`         | Log output folder             | `logs`                       | Custom path allowed                            |
| `ENV`             | Execution environment         | `development`                | `development` / `docker` / `production`        |
| `LOG_LEVEL`       | Logging verbosity             | `INFO`                       | `DEBUG` / `INFO` / `WARNING` / `ERROR`         |
| `BATCH_SIZE`      | PDFs to process before flush  | 50                           | Integer > 0                                    |
| `WORKERS`         | Parallel workers (Phase 5)    | 1                            | 1 to 8 (based on CPU cores)                    |

---

## Troubleshooting

### "tesseract not found"

```python
# Issue: Tesseract path not configured correctly

# Solution 1: Update .env
TESSERACT_PATH=/path/to/tesseract

# Solution 2: Test manually
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Path\To\tesseract.exe'
print(pytesseract.image_to_string(image))
```

### "poppler not found"

```python
# Issue: Poppler path not configured

# Solution 1: Update .env
POPPLER_PATH=/path/to/poppler/bin

# Solution 2: Test manually
from pdf2image import convert_from_path
images = convert_from_path("file.pdf", poppler_path=r'C:\path\to\poppler\Library\bin')
```

### "ModuleNotFoundError: No module named 'pytesseract'"

```bash
# Issue: Dependencies not installed

# Solution: Reinstall
pip install --upgrade pip
pip install -r requirements.txt
pip list | grep tesseract
```

### "Empty OCR output"

```bash
# Issue: Low DPI or obscured text

# Workarounds:
# 1. Check PDF DPI (should be 300+)
# 2. verify image quality
# 3. Adjust OCR parameters in src/config.py:
#    PSM (Page Segmentation Mode): 0-13
#    OEM (OCR Engine Mode): 0-3

# Test with specific parameters:
python -c "
import pytesseract
from pdf2image import convert_from_path
images = convert_from_path('file.pdf')
text = pytesseract.image_to_string(images[0], lang='eng', config='--psm 3 --oem 3')
print(text)
"
```

### "Out of memory with large batches"

```bash
# Issue: Too many PDFs processed simultaneously

# Solutions:
# 1. Reduce batch size in .env:
BATCH_SIZE=10

# 2. Use parallel pipeline (Phase 5):
WORKERS=4

# 3. Process in smaller chunks manually:
python -c "
from src.pipeline.orchestrator import ETLPipeline
import glob
pdfs = glob.glob('data/raw_reports/*.pdf')[:10]  # Process 10 at a time
pipeline = ETLPipeline()
pipeline.process_reports(pdfs)
"
```

---

## Docker Setup (Optional)

### Build Image

```bash
docker build -t medical-etl:latest .
```

### Run Container

```bash
docker run -v $(pwd)/data:/app/data \
           -v $(pwd)/logs:/app/logs \
           -e INPUT_DIR=/app/data/raw_reports \
           -e OUTPUT_DIR=/app/data/anonymized_reports \
           medical-etl:latest python main.py
```

### Docker Compose

```bash
docker-compose build
docker-compose up
```

---

## Next Steps

- ✅ **Setup complete?** Run `python main.py` with a test PDF
- 📚 **Learn more?** See [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)
- 🔨 **Build features?** See [DEVELOPMENT.md](DEVELOPMENT.md)
- 📊 **Production deploy?** See [DEPLOYMENT.md](DEPLOYMENT.md)
