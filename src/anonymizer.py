import re

def anonymize_text(text):
    """Anonymize PII fields in extracted text."""
    text = re.sub(r"Patient Name[:\s]+[\w\s]+", "Patient Name: [ANONYMIZED]", text)
    text = re.sub(r"Patient ID[:\s]+\w+", "Patient ID: [ANONYMIZED]", text)
    text = re.sub(r"Hospital Name[:\s]+[\w\s]+", "Hospital Name: [ANONYMIZED]", text)
    text = re.sub(r"Clinician[:\s]+[\w\s]+", "Clinician: [ANONYMIZED]", text)
    return text
