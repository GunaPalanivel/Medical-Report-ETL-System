# 🏥 Medical Report ETL System

A lightweight, production-ready ETL pipeline to **anonymize**, **extract**, and **structure** sensitive medical reports — built with real-world scalability, clean architecture, and modular Python design.

> 🔥 Designed for scanned PDFs, OCR-powered text extraction, metadata parsing, and secure anonymization — all wrapped into a beginner-friendly yet OSS-grade project.

---

## ✨ Features

- **🔒 Anonymization** — Redacts personal details like Patient Name, ID, Hospital, and Clinician.
- **🧠 Metadata Extraction** — Parses structured fields like Gestational Age, Age, BMI, and Clinical Findings.
- **📄 OCR Support** — Reads scanned PDFs using Tesseract OCR and Poppler.
- **📦 JSON Export** — Outputs standardized metadata JSONs ready for APIs, databases, or ML pipelines.
- **🛡️ Secure UUID Mapping** — Maintains anonymized ID consistency without leaking real identifiers.

---

## 🛠 Setup

### 1. Clone the repo

```bash
git clone https://github.com/GunaPalanivel/Medical-Report-ETL-System.git
```

```bash
cd Medical-Report-ETL-System
```

### 2. Install Dependencies

Make sure you have Python 3.10+ installed.

```bash
pip install -r requirements.txt
```

Required tools:

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/) (for PDF to image conversion)

> 📍 **Note:** Update the `POPPLER_PATH` and `tesseract_cmd` paths in `src/pdf_handler.py` and `main.py` according to your system setup.

### 3. Project Structure

```plaintext
src/
├── anonymizer.py     # Redacts personal info
├── extractor.py      # Parses structured metadata
├── json_writer.py    # Writes metadata JSON
├── pdf_handler.py    # OCR and PDF utilities
└── __init__.py       # Exposes clean imports

data/
├── raw_reports/      # Input folder for original PDFs
├── anonymized_reports/ # Output folder for anonymized PDFs
└── id_map.json       # Secure mapping of real IDs ➝ UUIDs

main.py               # Orchestrates the ETL flow
```

---

## 🚀 Usage

1. Place your scanned **medical reports** in `data/raw_reports/`.
2. Run the ETL script:

```bash
python main.py
```

This will:

- Extract text from each scanned PDF
- Anonymize sensitive fields
- Parse metadata fields
- Save anonymized PDFs to `data/anonymized_reports/`
- Save metadata JSON to `data/patient_metadata.json`
- Maintain a secure ID map at `data/id_map.json`

---

## 💡 Developer Tips

### Code Principles Followed

- **OOP**: Clear separation of concerns between modules.
- **SOLID**: Single Responsibility Principle (SRP) applied to each Python file.
- **Performance**: Optimized for batch processing (`O(n)`) across multiple PDFs.
- **Security**: UUID anonymization ensures no patient data leakage.

### Best Practices

- OCR can misread scanned PDFs depending on quality. Always verify extracted text manually for critical systems.
- `id_map.json` is your source of truth for linking real IDs to UUIDs. Protect it like a database secret key.
- For high-volume data, consider parallelizing OCR and anonymization using Python’s `concurrent.futures`.

---

## 📚 Resources

- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [FPDF Python Library](https://pyfpdf.readthedocs.io/en/latest/)
- [Regex 101](https://regex101.com/) — for tweaking metadata extraction patterns.

---

## 🙌 Contributing

If you spot improvements — better regexes, faster OCR configs, bugfixes — feel free to open a PR!
This project is beginner-friendly and a great first step into **open-source ETL systems**.

---
