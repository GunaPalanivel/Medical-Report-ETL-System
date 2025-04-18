import os
import re
import json
import uuid
from PyPDF2 import PdfReader, PdfWriter

def extract_metadata(text):
    metadata = {
        "patient_id": str(uuid.uuid4()),  # anonymized UUID
        "gestational_age": None,
        "age": None,
        "BMI": None,
        "findings": []
    }

    # ✅ Extract Gestational Age like "GA: 43 weeks 1 day"
    gest_age_match = re.search(r"GA[:\-]?\s*(\d+\s*weeks?\s*\d*\s*day[s]?)", text, re.IGNORECASE)
    if gest_age_match:
        metadata["gestational_age"] = gest_age_match.group(1).strip()

    # ✅ Extract Age like "Age: 33"
    age_match = re.search(r"Age[:\-]?\s*(\d+)", text, re.IGNORECASE)
    if age_match:
        metadata["age"] = int(age_match.group(1))

    # ✅ Extract BMI like "BMI: 28"
    bmi_match = re.search(r"BMI[:\-]?\s*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
    if bmi_match:
        metadata["BMI"] = float(bmi_match.group(1))

    # ✅ Extract Findings block (between "Examination Findings" and "Conclusion")
    findings_match = re.search(r"Examination Findings\s*(.*?)\s*Conclusion", text, re.DOTALL | re.IGNORECASE)
    if findings_match:
        findings_text = findings_match.group(1)
        metadata["findings"] = [line.strip() for line in findings_text.strip().split("\n") if line.strip()]

    return metadata
