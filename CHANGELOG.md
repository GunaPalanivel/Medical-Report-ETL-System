# Changelog

All notable changes to the Medical Report ETL System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Expand PII patterns (names, DOB, addresses)
- Modular architecture refactoring
- Unit test coverage
- Docker containerization

## [1.1.1] - 2026-02-05

### Fixed

- **Critical:** Fixed `src/_init_.py` broken exports (was exporting non-existent functions)
- **Dependencies:** Corrected `requirements.txt` (removed pandas, numpy, PyMuPDF, pdfminer.six, matplotlib, regex; added actual dependencies)

### Changed

- **Documentation:** Complete rewrite of all documentation to match actual v1.1.x codebase
- **README.md:** Removed fictional features, added "Current Limitations" section
- **CONTRIBUTING.md:** Simplified for actual flat-module architecture
- **SECURITY.md:** Updated to reflect 4 implemented PII patterns (not 8)
- **docs/SETUP.md:** Removed references to non-existent .env and Docker
- **docs/FEATURES.md:** Reduced from 12 fictional features to 7 actual features
- **docs/HIPAA_COMPLIANCE.md:** Honest about 4/18 Safe Harbor identifiers implemented

### Removed

- **docs/MODULAR_ARCHITECTURE.md** - Described fictional code structure
- **docs/PROJECT_STRUCTURE.md** - Showed non-existent directory tree
- **docs/DEVELOPMENT.md** - Referenced fictional plugin system
- **docs/PERFORMANCE.md** - Contained fabricated benchmarks
- **docs/DEPLOYMENT.md** - No Docker/Kubernetes files exist

### Added

- **docs/ROADMAP.md:** Future development roadmap (renamed from MODULAR_REFACTORING_GUIDE.md)
- **.gitignore:** Added exclusion for internal planning document

## [1.1.0] - 2026-02-04

### Added

- Comprehensive error handling in `main.py` with per-file recovery
- Input validation for directory existence and PDF file presence
- Results tracking with success/error counts and failed file list
- Exit codes for CI/CD integration (0 for success, 1 for failures)
- Processing summary with visual indicators (✅ ❌)
- Stack trace logging to stderr for debugging
- Continue-on-error logic for batch processing resilience

### Fixed

- **Critical:** Removed 43 lines of dead code (`write_anonymized_pdf()`) from `src/anonymizer.py`
- **Critical:** Fixed typo `"gestaional_age"` → `"gestational_age"` in `src/json_writer.py`
- **Data:** Migrated 50 patient records in `data/patient_metadata.json` to correct spelling

### Changed

- `main.py` refactored with `process_reports()` function for better error handling
- Error messages now include stage context (OCR, metadata, PDF generation)

### Security

- Verified `.gitignore` protects `id_map.json` from accidental commits

## [1.0.0] - 2026-01-15

### Added

- Initial release of Medical Report ETL System
- OCR text extraction from scanned PDFs using Tesseract at 300 DPI
- PII anonymization with regex-based pattern matching
- Metadata extraction for 5 clinical fields:
  - `gestational_age` (weeks)
  - `age` (patient age)
  - `bmi` (body mass index)
  - `findings` (clinical findings text)
  - `patient_id` (anonymized UUID)
- Anonymized PDF generation with redacted content
- JSON metadata export with structured schema
- UUID-based filename mapping for HIPAA compliance
- Batch processing for multiple PDF files

### Technical

- Python 3.8+ compatibility
- Dependencies: pytesseract, pdf2image, Pillow, fpdf
- External requirements: Tesseract OCR, Poppler

---

## Version History Summary

| Version | Date       | Highlights                                                    |
| ------- | ---------- | ------------------------------------------------------------- |
| 1.1.1   | 2026-02-05 | Documentation cleanup - removed fictional docs, fixed exports |
| 1.1.0   | 2026-02-04 | Emergency hotfix - 4 critical bugs fixed, error handling      |
| 1.0.0   | 2026-01-15 | Initial release - OCR, anonymization, metadata extraction     |

## Upgrade Guide

### 1.0.0 → 1.1.0

1. **Data Migration Required:**

   ```powershell
   # Run in PowerShell to fix existing patient_metadata.json
   (Get-Content data/patient_metadata.json) -replace '"gestaional_age":', '"gestational_age":' | Set-Content data/patient_metadata.json
   ```

2. **No Breaking API Changes** - Existing scripts will continue to work

3. **Recommended:** Update any downstream systems consuming `patient_metadata.json` to use the corrected `gestational_age` field name

---

[Unreleased]: https://github.com/GunaPalanivel/Medical-Report-ETL-System/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/GunaPalanivel/Medical-Report-ETL-System/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/GunaPalanivel/Medical-Report-ETL-System/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/GunaPalanivel/Medical-Report-ETL-System/releases/tag/v1.0.0
