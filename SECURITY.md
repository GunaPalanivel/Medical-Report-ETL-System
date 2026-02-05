# Security Policy

## Overview

The Medical Report ETL System processes sensitive healthcare data (PHI - Protected Health Information). Security is a core requirement, not an afterthought.

This document outlines our security practices and how to report vulnerabilities.

---

## Supported Versions

| Version | Supported              | Notes            |
| ------- | ---------------------- | ---------------- |
| 1.1.x   | ✅ Yes                 | Current release  |
| 1.0.x   | ⚠️ Security fixes only | Upgrade to 1.1.1 |
| < 1.0   | ❌ No                  | End of life      |

---

## Reporting a Vulnerability

### DO NOT create public GitHub issues for security vulnerabilities

If you discover a security vulnerability, please report it responsibly:

### Option 1: GitHub Security Advisories (Preferred)

1. Go to [Security Advisories](https://github.com/GunaPalanivel/Medical-Report-ETL-System/security/advisories)
2. Click "Report a vulnerability"
3. Provide detailed information (see below)

### Option 2: Private Email

Email: **security@[project-domain].com** (or maintainer's email)

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

### Response Timeline

| Action             | Timeline              |
| ------------------ | --------------------- |
| Acknowledgment     | Within 48 hours       |
| Initial assessment | Within 1 week         |
| Fix development    | Depends on severity   |
| Security advisory  | After fix is released |

---

## Security Considerations

### Data Classification

| Data Type               | Classification      | Protection                     |
| ----------------------- | ------------------- | ------------------------------ |
| Raw PDFs (PHI)          | **HIPAA Protected** | Never committed to git         |
| `id_map.json`           | **Confidential**    | Git-ignored, encrypted at rest |
| `patient_metadata.json` | **De-identified**   | Safe for research use          |
| Anonymized PDFs         | **De-identified**   | Safe for sharing               |
| Source code             | Public              | Open source                    |

### What We Protect

1. **Patient Health Information (PHI)**
   - Names, addresses, dates of birth
   - Medical record numbers (MRN)
   - Social Security numbers
   - All 18 HIPAA identifiers

2. **UUID Mapping File (`id_map.json`)**
   - Links anonymized IDs back to originals
   - NEVER commit to version control
   - Protected by `.gitignore`

3. **Configuration Secrets**
   - API keys
   - Database credentials
   - Encryption keys

### Built-in Security Features

| Feature                | Status         | Location                    |
| ---------------------- | -------------- | --------------------------- |
| PII Redaction          | ✅ 4 patterns  | `src/anonymizer.py`         |
| UUID De-identification | ✅ Implemented | `main.py` (uuid generation) |
| Audit Logging          | ⏳ Planned     | Not yet implemented         |
| Input Validation       | ⏳ Planned     | Not yet implemented         |
| Atomic Writes          | ⏳ Planned     | Not yet implemented         |
| Encryption at Rest     | ⏳ Planned     | Not yet implemented         |

> **Note:** Features marked "Planned" are on the [roadmap](docs/ROADMAP.md) for future releases.

---

## Security Best Practices

### For Developers

```python
# ❌ NEVER log PHI
logger.info(f"Processing patient: {patient_name}")  # BAD

# ✅ DO log anonymized identifiers
logger.info(f"Processing patient: {uuid}")  # GOOD
```

```python
# ❌ NEVER hardcode secrets
api_key = "sk-abc123..."  # BAD

# ✅ DO use environment variables
api_key = os.environ.get("API_KEY")  # GOOD
```

```python
# ❌ NEVER commit sensitive files
# Make sure .gitignore includes:
# - id_map.json
# - data/raw_reports/
# - *.env
# - .env.*
```

### For Operators

1. **Encrypt at Rest**

   ```bash
   # Encrypt id_map.json
   gpg --symmetric --cipher-algo AES256 id_map.json
   ```

2. **Restrict File Permissions**

   ```bash
   chmod 600 id_map.json
   chmod 700 data/raw_reports/
   ```

3. **Use Secure Transfer**
   - Always use HTTPS/SFTP for file transfers
   - Never email PHI without encryption

4. **Audit Access**
   - Enable structured logging
   - Review access logs regularly
   - Set up alerts for anomalies

---

## HIPAA Compliance

This system is designed to support HIPAA Safe Harbor de-identification:

### 18 HIPAA Identifiers — Current Coverage

> **Current Status:** 4 of 18 identifiers are actively redacted. See [docs/ROADMAP.md](docs/ROADMAP.md) for planned expansion.

| #   | Identifier                      | Status            |
| --- | ------------------------------- | ----------------- |
| 1   | Names                           | ✅ Redacted       |
| 2   | Geographic data                 | ⏳ Not yet        |
| 3   | Dates (except year)             | ⏳ Not yet        |
| 4   | Phone numbers                   | ⏳ Not yet        |
| 5   | Fax numbers                     | ⏳ Not yet        |
| 6   | Email addresses                 | ⏳ Not yet        |
| 7   | Social Security numbers         | ⏳ Not yet        |
| 8   | Medical record numbers          | ⏳ Not yet        |
| 9   | Health plan beneficiary numbers | ⏳ Not yet        |
| 10  | Account numbers                 | ⏳ Not yet        |
| 11  | Certificate/license numbers     | ⏳ Not yet        |
| 12  | Vehicle identifiers             | ⏳ Not yet        |
| 13  | Device identifiers              | ⏳ Not yet        |
| 14  | Web URLs                        | ⏳ Not yet        |
| 15  | IP addresses                    | ⏳ Not yet        |
| 16  | Biometric identifiers           | N/A (not in PDFs) |
| 17  | Full-face photos                | N/A (text only)   |
| 18  | Any unique identifying number   | ⏳ Not yet        |

**Currently Implemented Patterns (v1.1.1):**

- Patient Name
- Patient ID
- Hospital Name
- Clinician Name

See [docs/HIPAA_COMPLIANCE.md](docs/HIPAA_COMPLIANCE.md) for detailed compliance documentation.

---

## Threat Model

### In Scope

| Threat                 | Mitigation                            |
| ---------------------- | ------------------------------------- |
| PHI exposure in logs   | No PHI logging policy                 |
| PHI in version control | `.gitignore` for sensitive files      |
| UUID mapping exposure  | File encryption, access controls      |
| Incomplete redaction   | Multiple pattern matching, validation |
| Output file corruption | Atomic writes                         |

### Out of Scope

| Threat             | Reason                     |
| ------------------ | -------------------------- |
| Network attacks    | Deploy behind firewall/VPN |
| Server compromise  | Use OS-level security      |
| Physical access    | Physical security controls |
| Social engineering | User training              |

---

## Security Checklist

Before deploying to production:

- [ ] All PHI logging disabled
- [ ] `id_map.json` in `.gitignore`
- [ ] `data/raw_reports/` in `.gitignore`
- [ ] File permissions restricted (600/700)
- [ ] Encryption enabled for sensitive files
- [ ] Audit logging configured
- [ ] Access controls implemented
- [ ] HIPAA BAA in place (if applicable)
- [ ] Security review completed

---

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be acknowledged (with permission) in our security advisories.

---

## Contact

- **Security Issues**: Use [GitHub Security Advisories](https://github.com/GunaPalanivel/Medical-Report-ETL-System/security/advisories)
- **General Questions**: [GitHub Discussions](https://github.com/GunaPalanivel/Medical-Report-ETL-System/discussions)
- **Maintainer**: [@GunaPalanivel](https://github.com/GunaPalanivel)
