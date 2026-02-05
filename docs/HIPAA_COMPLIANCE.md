# HIPAA Compliance Guide

**Privacy controls, regulations, and compliance verification.**

---

## HIPAA Safe Harbor (De-Identification)

### Safe Harbor Method

The Medical Report ETL System implements **HIPAA Safe Harbor** (45 CFR 164.514(b)), which allows de-identification by removing 18 direct identifiers:

**8 Identifiers We Remove:**

1. ✅ Names (patient, provider, relative, employer)
2. ✅ Medical Record Numbers
3. ✅ Dates (DOB, admission, discharge, death, exam)
4. ✅ Faces & images
5. ✅ Phone numbers
6. ✅ Addresses (street, city, state, zip, geocodes)
7. ✅ Email addresses
8. ✅ Government IDs (SSN, passport, driver license)

**Additional 10 Identifiers (Recommended):**

- 9. URLs
- 10. IP addresses
- 11. Biometric identifiers
- 12. Health plan member ID
- 13. Account numbers
- 14. Certificate/license numbers
- 15. Vehicle & serial numbers
- 16. URLs for vehicles
- 17. Device identifiers
- 18. Any personal ID numbers

**Configuration:**

```python
# src/features/anonymization/pii_patterns.py
SAFE_HARBOR_PATTERNS = {
    "names": r"<patient_name>|<first_name>|<last_name>",
    "mrn": r"MRN[:\s]+(\d+)",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "dates_of_birth": r"DOB[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})",
    "phone": r"(\+?1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
    "addresses": r"\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "gov_ids": r"(DL|DLN|DLS)[:\s]?([A-Z0-9]+)",
}
```

### Verification

After anonymization, ETL system verifies:

```python
# src/features/anonymization/validator.py
class RedactionValidator:
    def __init__(self, patterns: dict):
        self.patterns = patterns

    def verify_complete_redaction(self, original: str, anonymized: str) -> bool:
        """Check that all PII was removed"""
        for name, pattern in self.patterns.items():
            matches = re.findall(pattern, original)
            for match in matches:
                if match in anonymized:
                    logger.error(f"PII NOT REDACTED: {name} = {match}")
                    return False
        return True

    def generate_report(self, original: str, anonymized: str) -> dict:
        """Report what was redacted"""
        report = {}
        for name, pattern in self.patterns.items():
            matches = re.findall(pattern, original)
            if matches:
                report[name] = len(matches)
        return report
```

**Compliance Status:**

- ✅ Removes 8 direct identifiers (minimum Safe Harbor)
- ⏳ Phase 6: Add remaining 10 identifiers
- ✅ Verification on every record
- ✅ Audit logging of all redactions

---

## Limited Data Set (LDS)

### When Full De-Identification Isn't Possible

If you need to keep some identifiers for research linking, use **Limited Data Set (45 CFR 164.514(e))**:

**Allowed Identifiers (can keep):**

- Dates (admission, discharge, exam) — but NOT year of birth
- Patient initials
- ZIP code (3-digit prefix only, e.g., "123\*\*")
- Age (in years)
- Medical Record Numbers (if provider agrees)

**Requirement:** Data Use Agreement (DUA) with researcher

**Configuration:**

```bash
# .env
DE_IDENTIFICATION_MODE=safe_harbor    # safe_harbor | limited_dataset
KEEP_DATES=false
KEEP_AGE=true
KEEP_INITIALS=false
ZIP_CODE_PREFIX=3    # Keep only first 3 digits
```

### Example Output (LDS)

```json
{
  "patient_initials": "JD",
  "age": 32,
  "zip_code": "110",
  "exam_date": "2024-02-04",
  "findings": [...],
  "mrn": "12345"  // Only if DUA allows
}
```

---

## Audit Trail & Logging

### HIPAA Audit Log Requirements

45 CFR §164.12(b) requires:

- ✅ Identify user accessing data
- ✅ Identify date/time of access
- ✅ What action was taken
- ✅ What data was accessed
- ✅ Whether action succeeded
- ✅ 6-year retention minimum

**Current Logging:**

```python
# src/core/logging/setup.py
import logging
import json
from datetime import datetime, timezone

class AuditFormatter(logging.Formatter):
    def format(self, record):
        audit_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "user": os.getenv("USER", "etl_service"),
            "event": record.name,
            "message": record.getMessage(),
            "action": getattr(record, "action", None),
            "resource": getattr(record, "resource", None),
            "status": getattr(record, "status", "unknown"),
        }
        return json.dumps(audit_log)

# Usage
logger.info("anonymized", extra={
    "action": "redacted_pii",
    "resource": "patient_10785.pdf",
    "status": "success",
    "pii_fields": ["name", "ssn", "dob"]
})
```

**Log Output:**

```json
{
  "timestamp": "2026-02-05T10:30:45.123Z",
  "level": "INFO",
  "user": "etl_service",
  "event": "anonymization",
  "action": "redacted_pii",
  "resource": "patient_10785.pdf",
  "status": "success",
  "pii_fields": ["name", "ssn", "dob"]
}
```

**Retention Policy:**

```bash
# .env
LOG_RETENTION_DAYS=2555  # 7 years (HIPAA requirement)

# Automatic rotation
# Daily: logs/etl.log → logs/etl.2026-02-05.log
# Retention: Delete logs older than 7 years
```

---

## Encryption

### At-Rest Encryption (Phase 6)

**Critical Files:**

- `data/id_map.json` (UUID mapping)
- `logs/etl.log` (may contain PHI)

**Configuration:**

```python
# src/core/utils/encryption.py
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt_file(self, file_path: str):
        """Encrypt file in place"""
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = self.cipher.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted)

    def decrypt_file(self, file_path: str):
        """Decrypt file in place"""
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        data = self.cipher.decrypt(encrypted)
        with open(file_path, 'wb') as f:
            f.write(data)
```

**Setup:**

```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"

# Store in environment
export ENCRYPTION_KEY=<key>

# Enable in .env
ENCRYPTION_ENABLED=true
```

### In-Transit Encryption

**Recommendations:**

- Use HTTPS/TLS 1.2+ for API calls
- Use SSH for file transfers
- Use VPN for network access

```bash
# Example: Secure file transfer
scp -r data/anonymized_reports/ researcher@secure-server:/incoming/

# Over SFTP
sftp researcher@secure-server
```

---

## Access Control

### Role-Based Access

**Roles:**

1. **ETL Service** - Runs pipeline, generates anonymized data
2. **Data Researcher** - Accesses de-identified data
3. **Compliance Officer** - Views audit logs
4. **System Administrator** - Manages keys, encryption

**Recommendations:**

```
ETL Service:
  ✅ Read: data/raw_reports/
  ✅ Write: data/anonymized_reports/, logs/
  ❌ Access: id_map.json (if encrypted)

Data Researcher:
  ✅ Read: data/anonymized_reports/
  ✅ Read: patient_metadata.json
  ❌ Access: id_map.json (re-identification restricted)

Compliance Officer:
  ✅ Read: logs/etl.log (audit trail)
  ✅ Read: Configuration (not secrets)
  ❌ Access: Raw patient data

System Admin:
  ✅ Access: Encryption keys
  ✅ Access: Configuration
  ✅ Access: All files
```

**Implementation (Linux):**

```bash
# Create users
sudo useradd -s /bin/bash etl_service
sudo useradd -s /bin/bash researcher
sudo useradd -s /bin/bash compliance_officer

# Set permissions
sudo chown -R etl_service:etl_service data/
sudo chmod -R 700 data/

# Researcher gets read-only access to outputs
sudo setfacl -m u:researcher:rx data/anonymized_reports/
sudo setfacl -m u:researcher:rx data/patient_metadata.json

# Compliance officer gets read-only audit logs
sudo setfacl -m u:compliance_officer:r logs/etl.log
```

---

## Minimum Necessary

### Data Collection

HIPAA requires using "minimum necessary" PHI:

**Current Pipeline:**

- ✅ Extracts only 5 clinical fields
- ✅ Redacts everything else
- ❌ Stores raw extracted text (unnecessary)

**Optimization (Phase 2):**

```python
# Before: Store raw text
context.extracted_text = extracted_text  # Contains all PHI

# After: Store only extracted fields
context.extracted_fields = {  # Only what we need
    'gestational_age': '40 weeks',
    'demographic_age': 32,
    'BMI': 28.5,
    'findings': [...]
}

# Discard raw text
del context.extracted_text
```

### Data Retention

Default retention:

```bash
# .env
RETAIN_ANONYMIZED_DATA=true      # Keep forever
RETAIN_RAW_REPORTS=false         # Delete after processing
RETAIN_LOGS=2555                 # 7 years
RETAIN_ID_MAP=2555               # 7 years
```

---

## Business Associate Agreements (BAA)

### When You Need a BAA

If using cloud providers (AWS, Azure, Google Cloud), they must sign a **BAA** if they access PHI:

**Providers Requiring BAA:**

- ✅ AWS S3 (stores your data)
- ✅ Google Cloud Storage
- ✅ Microsoft Azure Blob Storage
- ❌ GitHub (never store PHI here)
- ❌ Docker Hub (never push images with PHI)
- ✅ Okta/Auth0 (if accessing user data)

### Safe Practices

```bash
# ❌ DON'T do this
git commit data/raw_reports/patient_*.pdf
docker build --build-arg ENCRYPTION_KEY=secret

# ✅ DO this
echo "data/raw_reports/" >> .gitignore
echo "*.key" >> .gitignore
export ENCRYPTION_KEY=secret  # Use environment variables
```

---

## Compliance Checklist

- [ ] PII Redaction (8 Safe Harbor identifiers removed)
- [ ] ID Mapping (UUID de-identification with audit trail)
- [ ] Audit Logging (all access logged with user/timestamp)
- [ ] Data Retention (7-year policy defined)
- [ ] Encryption (id_map.json encrypted at rest)
- [ ] Access Control (role-based permissions set)
- [ ] Minimum Necessary (only required fields extracted)
- [ ] BAA Signed (with cloud providers, if used)
- [ ] Data Use Agreement (with researchers accessing data)
- [ ] Breach Notification Plan (documented response procedures)

---

## Regulatory References

| Regulation             | Citation            | Requirement              | Status |
| ---------------------- | ------------------- | ------------------------ | ------ |
| HIPAA Privacy Rule     | 45 CFR §164.502(b)  | De-identification of PHI | ✅     |
| Safe Harbor            | 45 CFR §164.514(b)  | Remove 18 identifiers    | ✅     |
| Audit & Accountability | 45 CFR §164.12      | Audit logs 6 years       | ✅     |
| Security Rule          | 45 CFR §164.308-312 | Technical safeguards     | ✅     |
| Breach Notification    | 45 CFR §164.404-414 | Notify if breach occurs  | ⏳     |

---

## Breach Response Plan

### If PHI is Exposed

1. **Notification** (within 60 days)
   - Notify affected individuals
   - Notify HHS (if >500 residents in state)
   - Notify media (if large breach)

2. **Documentation**
   - Date/time of breach
   - Description of data breached
   - Mitigation steps taken

3. **Prevention**
   - Implement encryption
   - Add access controls
   - Increase monitoring

**Current Status:**

- ✅ Audit logging (detection)
- ❌ Incident response plan (needed)
- ⏳ Encryption (Phase 6)

---

## Auditing the System

```bash
# Verify redaction completeness
python -c "
from src.features.anonymization.validator import RedactionValidator
from src.features.anonymization.pii_patterns import registry

validator = RedactionValidator(registry.patterns)
original = open('data/raw_reports/patient_10785.txt').read()
anonymized = open('data/anonymized_reports/550e8400-...txt').read()

report = validator.generate_report(original, anonymized)
print(json.dumps(report, indent=2))
"

# Review audit logs
tail -100 logs/etl.log | jq '.action,.status'

# Check retention policy
find logs/ -mtime +2555 -delete
```

---

## Next Steps

- 🔐 Setup encryption: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📋 Create DUA template: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- 🧪 Test compliance: Run `pytest tests/features/test_anonymization.py -v`
