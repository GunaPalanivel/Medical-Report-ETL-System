# Roadmap

> Future development plans for the Medical Report ETL System

---

## Current State (v2.0.0)

The system is a working ETL pipeline that:

- Extracts text from scanned PDFs using Tesseract OCR
- Anonymizes 4 PII patterns (patient name, patient ID, hospital, clinician)
- Extracts 5 metadata fields
- Generates anonymized PDFs and JSON output
- Phase 1 modular refactor is in progress (core, features, pipeline)

See [FEATURES.md](FEATURES.md) for complete documentation of current capabilities.

---

## Short-Term Goals (v1.2.0)

**Target: Expand PII coverage**

### Additional PII Patterns

| Pattern         | Priority | Complexity |
| --------------- | -------- | ---------- |
| Patient names   | High     | Medium     |
| Dates of birth  | High     | Low        |
| Addresses       | Medium   | High       |
| Account numbers | Medium   | Low        |

### Improved Validation

- [ ] Input PDF validation before processing
- [ ] Better error messages for OCR failures
- [ ] Detailed processing logs

---

## Phase 1 Goals (v2.0.0) — Completed

**Target: Modular architecture**

### Infrastructure Layer (`src/core/`)

- Configuration management via environment variables ✅
- Structured logging with rotation ✅
- Custom exception hierarchy ✅
- Utility functions (retry, validation, atomic writes) ✅

### Feature Layer (`src/features/`)

- **OCR Engine**: Pluggable OCR backends ✅
- **PII Registry**: Plugin system for adding patterns without code changes ✅
- **Metadata Extractors**: Strategy pattern for field extraction ✅

### Pipeline Layer (`src/pipeline/`)

- Stage-based processing with context passing ✅
- Per-stage error handling ✅
- Processing reports and metrics ✅

### Benefits

| Aspect             | v1.x                   | v2.0                   |
| ------------------ | ---------------------- | ---------------------- |
| Adding PII pattern | Edit anonymizer.py     | Register via registry  |
| Testing components | Requires full pipeline | Independent unit tests |
| Code organization  | 4 flat files           | Layered architecture   |
| Error handling     | Basic try/except       | Exception hierarchy    |

---

## Long-Term Goals (v3.0.0)

**Target: Production-ready deployment**

### Testing

- [ ] Unit test coverage (target: 80%+)
- [ ] Integration tests with sample PDFs
- [ ] Performance benchmarks

### Deployment

- [ ] Docker containerization
- [ ] Environment-based configuration
- [ ] CI/CD pipeline with GitHub Actions

### HIPAA Compliance

- [ ] Expand to all 18 Safe Harbor identifiers
- [ ] Audit logging
- [ ] Data retention policies

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to help with roadmap items.

### Priority Labels

- **P0**: Critical for next release
- **P1**: Important, schedule when possible
- **P2**: Nice to have, community contributions welcome

---

## Version History

| Version | Focus                     | Status      |
| ------- | ------------------------- | ----------- |
| 1.0.0   | Initial release           | Released    |
| 1.1.0   | Bug fixes, error handling | Released    |
| 1.1.1   | Documentation cleanup     | Released    |
| 1.2.0   | Expanded PII patterns     | Planned     |
| 2.0.0   | Modular architecture      | Current     |
| 3.0.0   | Production deployment     | Future      |
