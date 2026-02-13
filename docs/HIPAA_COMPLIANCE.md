# HIPAA Compliance Guide

**Privacy considerations for the Medical Report ETL System.**

> **Important:** This document describes privacy controls. For technical implementation details, see [FEATURE_ANALYSIS.md](FEATURE_ANALYSIS.md). Some features are implemented (✅), others are planned (⏳).

---

## Current Implementation Status

| Feature                  | Status         | Notes                                         |
| ------------------------ | -------------- | --------------------------------------------- |
| PII Redaction            | ✅ 4 patterns  | Patient Name, Patient ID, Hospital, Clinician |
| UUID De-identification   | ✅ Implemented | Random UUID per report                        |
| Secure File Storage      | ✅ .gitignore  | id_map.json excluded from git                 |
| Additional PII Patterns  | ⏳ Planned     | SSN, DOB, phone, email, address, etc.         |
| Encryption at Rest       | ⏳ Planned     | AES-256 for id_map.json                       |
| Structured Audit Logging | ⏳ Planned     | JSON format with timestamps                   |
| Access Controls          | ⏳ Planned     | Role-based permissions                        |

---

## HIPAA Safe Harbor (De-Identification)

### Safe Harbor Method Overview

HIPAA Safe Harbor (45 CFR 164.514(b)) allows de-identification by removing 18 direct identifiers.

### Current PII Redaction (v1.1.1)

**4 Patterns Implemented:**

| #   | Identifier     | Regex Pattern                               | Status         |
| --- | -------------- | ------------------------------------------- | -------------- |
| 1   | Patient Name   | `Patient Name[:\s]+[A-Za-z][A-Za-z\s]+`     | ✅ Implemented |
| 2   | Patient ID     | `Patient ID[:\s]+[A-Za-z0-9][A-Za-z0-9_-]*` | ✅ Implemented |
| 3   | Hospital Name  | `Hospital Name[:\s]+[A-Za-z][A-Za-z\s]+`    | ✅ Implemented |
| 4   | Clinician Name | `Clinician[:\s]+[A-Za-z][A-Za-z\s]+`        | ✅ Implemented |

**Implementation:** [src/features/anonymization/pii_patterns.py](../src/features/anonymization/pii_patterns.py)

```python
from src.features.anonymization import PIIRedactor, build_default_registry

registry = build_default_registry()
redactor = PIIRedactor(registry.get_all())

text = "Patient Name: John Doe, Patient ID: 12345"
anonymized = redactor.redact(text)
```

### Planned Additional Patterns

| #   | Identifier             | Status     | Target         |
| --- | ---------------------- | ---------- | -------------- |
| 5   | SSN                    | ⏳ Planned | Future release |
| 6   | Phone numbers          | ⏳ Planned | Future release |
| 7   | Email addresses        | ⏳ Planned | Future release |
| 8   | Dates (DOB, etc.)      | ⏳ Planned | Future release |
| 9   | Addresses              | ⏳ Planned | Future release |
| 10  | Medical Record Numbers | ⏳ Planned | Future release |

See [ROADMAP.md](ROADMAP.md) for implementation timeline.

---

## UUID De-Identification

**Status:** ✅ Implemented

The system maps original filenames to random UUIDs:

```
Original: patient_10785.pdf
Output:   550e8400-e29b-41d4-a716-446655440000.pdf
Mapping:  data/id_map.json (protected by .gitignore)
```

**Security considerations:**

- `id_map.json` contains the UUID↔original mapping
- This file is excluded from git via `.gitignore`
- Anyone with this file can re-identify patients
- Store securely with restricted access

**Planned enhancement:** AES-256 encryption for `id_map.json`

---

## Data Classification

| Data Type               | Classification      | Current Protection | Planned                      |
| ----------------------- | ------------------- | ------------------ | ---------------------------- |
| Raw PDFs (PHI)          | **HIPAA Protected** | Manual handling    | Auto-delete after processing |
| `id_map.json`           | **Confidential**    | .gitignore         | + AES-256 encryption         |
| `patient_metadata.json` | **De-identified**   | Safe for research  | —                            |
| Anonymized PDFs         | **De-identified**   | Safe for sharing   | —                            |
| Source code             | Public              | Open source        | —                            |

---

## Current Security Measures

### What's Protected Now

1. **Version Control Protection**
   - `id_map.json` in `.gitignore`
   - `data/raw_reports/` in `.gitignore`
   - `.env` files in `.gitignore`

2. **PII Redaction**
   - 4 patterns actively redacting PHI
   - Replacement text clearly marked as `[ANONYMIZED]`

3. **De-identification**
   - UUID-based filenames
   - Original filenames never appear in output

### Best Practices (Manual)

Until automated controls are implemented:

```powershell
# Windows: Restrict file permissions
icacls "data\id_map.json" /inheritance:r /grant:r "$env:USERNAME:(R)"

# Never share id_map.json
# Never commit raw_reports/ to git
# Delete raw PDFs after processing (manual step)
```

---

## Planned Security Enhancements

### Phase 6: Encryption at Rest

```python
# Planned implementation
from cryptography.fernet import Fernet

# Encrypt id_map.json
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(open('id_map.json', 'rb').read())
```

### Phase 6: Structured Audit Logging

```json
// Planned log format
{
  "timestamp": "2026-02-05T10:30:45Z",
  "action": "anonymize",
  "input": "patient_10785.pdf",
  "output": "550e8400-...",
  "status": "success"
}
```

See [ROADMAP.md](ROADMAP.md) for full implementation plan.

---

## HIPAA Compliance Checklist

### Currently Implemented

- [x] PII redaction (4 patterns)
- [x] UUID de-identification
- [x] Sensitive files in .gitignore
- [x] Anonymized output clearly marked

### Planned (Not Yet Implemented)

- [ ] Full Safe Harbor compliance (18 identifiers)
- [ ] Encryption at rest (id_map.json)
- [ ] Structured audit logging
- [ ] Role-based access controls
- [ ] Automatic data retention policies
- [ ] Breach notification procedures

---

## Regulatory References

| Regulation             | Citation            | Requirement              | Status     |
| ---------------------- | ------------------- | ------------------------ | ---------- |
| HIPAA Privacy Rule     | 45 CFR §164.502(b)  | De-identification of PHI | ⚠️ Partial |
| Safe Harbor            | 45 CFR §164.514(b)  | Remove 18 identifiers    | ⚠️ 4 of 18 |
| Audit & Accountability | 45 CFR §164.312(b)  | Audit logs 6 years       | ⏳ Planned |
| Security Rule          | 45 CFR §164.308-312 | Technical safeguards     | ⏳ Planned |

---

## Recommendations

### For Production Use

1. **Add more PII patterns** before processing sensitive data
2. **Encrypt** `id_map.json` manually until automated encryption is implemented
3. **Restrict access** to the `data/` directory
4. **Delete raw PDFs** after processing
5. **Review output** manually to verify redaction completeness

### Example Manual Encryption

```powershell
# Windows: Use 7-Zip with AES-256
7z a -p -mhe=on id_map.7z id_map.json
Remove-Item id_map.json
```

---

## Disclaimer

> **This system provides tools for PHI de-identification but does not guarantee HIPAA compliance.** Organizations are responsible for:
>
> - Implementing additional safeguards as needed
> - Verifying redaction completeness
> - Maintaining proper access controls
> - Following organizational security policies
> - Consulting with compliance officers

---

## Next Steps

- **Add PII patterns:** See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-pii-patterns)
- **View roadmap:** See [ROADMAP.md](ROADMAP.md)
- **Setup guide:** See [SETUP.md](SETUP.md)
