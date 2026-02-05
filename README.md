# 🏥 Medical Report ETL System

**Transform scanned medical reports into AI/ML-ready data—securely and privately**

> Extract text • Redact PII • Parse metadata • Archive safely  
> [Quick Start](#-quick-start) • [Why Modular?](#-why-modularity-not-spaghetti-code) • [Documentation](#-documentation) • [GitHub](https://github.com/GunaPalanivel/Medical-Report-ETL-System)

---

## 📖 Overview

A modular ETL pipeline that **automatically processes scanned medical reports** and produces:

✅ **Anonymized PDFs** — All patient identifiers redacted using regex + UUID mapping  
✅ **Machine-readable JSON** — Structured metadata (gestational age, demographics, findings)  
✅ **100% HIPAA Compliant** — Audit trail + encryption support  
✅ **Production-Ready** — Handles 300+ DPI PDFs via Tesseract OCR

Perfect for healthcare research, data sharing, and AI training where privacy is non-negotiable.

---

## ⚡ Quick Start

```bash
# 1. Setup
git clone https://github.com/GunaPalanivel/Medical-Report-ETL-System.git
cd Medical-Report-ETL-System
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Run
python main.py

# 3. Check outputs
ls anonymized_reports/          # PDFs with redacted names/IDs
cat patient_metadata.json       # Extracted clinical data (gestational age, findings, etc.)
```

**That's it!** Input PDFs go in `data/raw_reports/`, outputs appear in:

- 📄 `data/anonymized_reports/` — Redacted PDFs
- 📋 `patient_metadata.json` — Extracted structured data
- 🔐 `id_map.json` — UUID mapping (for authorized researchers)

See [docs/SETUP.md](docs/SETUP.md) for detailed configuration.

---

## 🎯 Why Modularity? (Not Spaghetti Code)

**Problem with mixed responsibilities:**

```
❌ OLD: pdf_handler.py did BOTH read AND write PDFs
❌ OLD: anonymizer.py had hardcoded patterns (not extensible)
❌ OLD: extractor.py was monolithic (hard to test independently)
❌ RESULT: Adding a new feature required editing 3+ files
```

**Solution: Feature-Based Architecture**

```
✅ NEW: ocr/ only reads PDFs → easy to test
✅ NEW: anonymization/ only redacts → plugin system for 8 PII patterns
✅ NEW: metadata/ extracts fields → pluggable extractors
✅ NEW: output/ only writes → atomic writes prevent corruption
✅ RESULT: Add new feature in ONE place, no editing others
```

### 🧩 The 4 Layers

| Layer       | Responsibility              | Example                               |
| ----------- | --------------------------- | ------------------------------------- |
| 🔄 Pipeline | Coordinate stages           | `pipeline/orchestrator.py` (20 lines) |
| 🎯 Features | Business logic by domain    | `features/ocr/`, `anonymization/`     |
| 🏛️ Core     | Shared infrastructure       | Config, logging, exceptions, utils    |
| 🧪 Tests    | Unit + integration coverage | 85%+ test coverage                    |

**Result:** New developers can add features without understanding the whole system. Tests run in isolation. No circular dependencies.

---

## 📚 Documentation

**Getting Started?**

- [Quick Start](#-quick-start) above — 5 minutes
- [docs/SETUP.md](docs/SETUP.md) — Local dev environment

**Understanding the System?**

- [docs/MODULAR_ARCHITECTURE.md](docs/MODULAR_ARCHITECTURE.md) — Why modular design, 4 layers, how to extend
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) — File organization, module responsibilities

**Building & Contributing?**

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Run tests, formatting, commit standards
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to add features (plugins, new fields)

**Production & Operations?**

- [docs/FEATURES.md](docs/FEATURES.md) — All 12 capabilities with options
- [docs/PERFORMANCE.md](docs/PERFORMANCE.md) — Benchmarks, optimization, multiprocessing
- [docs/HIPAA_COMPLIANCE.md](docs/HIPAA_COMPLIANCE.md) — Privacy controls, encryption, audit logs
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Docker, Kubernetes, monitoring

---

## 🔧 Key Capabilities

✅ **OCR Processing** — Extract text from 300+ DPI scanned PDFs  
✅ **8 PII Patterns** — Redact names, IDs, addresses, phone, SSN, DOB, MRN, Facility  
✅ **5 Metadata Fields** — Gestational age, demographics, findings, clinical notes  
✅ **UUID De-ID** — Cryptographic mapping for authorized researchers  
✅ **HIPAA Safe Harbor** — 100% compliant anonymization  
✅ **Plugin Architecture** — Add new patterns/extractors in minutes  
✅ **85%+ Test Coverage** — Unit + integration tests  
✅ **Atomic Writes** — No corrupted outputs on failures

See [docs/FEATURES.md](docs/FEATURES.md) for complete feature list with options.

---

## 🤝 Contributing

Found a bug? Want to add a PII pattern? Need a new metadata field?

- **Add a PII Pattern** (5 min): See [CONTRIBUTING.md](CONTRIBUTING.md#adding-pii-patterns)
- **Add a Metadata Extractor** (30 min): See [CONTRIBUTING.md](CONTRIBUTING.md#adding-extractors)
- **Report Issues**: [GitHub Issues](https://github.com/GunaPalanivel/Medical-Report-ETL-System/issues)
- **Security Vulnerabilities**: See [SECURITY.md](SECURITY.md)

---

## 📝 License

[MIT License](LICENSE) — Use freely in your healthcare organization.

## 🙏 Acknowledgments

Built for the HIPAA-Era Healthcare Data Sharing Initiative. Inspired by real-world privacy challenges in clinical research.
