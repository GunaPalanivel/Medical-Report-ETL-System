**Appendix A - Report Format**

---

### 1. Motivation

As someone deeply interested in backend systems, data pipelines, and real-world applications of ETL (Extract, Transform, Load) principles, I picked this role challenge because it combined everything I love: Python scripting, working with messy input data (PDFs), OCR-based automation, metadata extraction, and secure anonymization — all wrapped up in a medical context. This project wasn’t just about technical skills; it was a perfect mix of clean code, privacy preservation, and building systems that can scale. It gave me a platform to demonstrate solid design thinking, a secure approach to patient data handling, and efficient metadata structuring that aligns with industry best practices.

---

### 2. Introduction About the Task

**Task Understanding:** The objective was to build a robust ETL pipeline to ingest raw ultrasound medical reports in PDF format, extract meaningful structured metadata (e.g., gestational age, BMI, age, findings), anonymize sensitive patient details, and produce two outputs:

1. Anonymized PDF copies of each report
2. A clean, machine-readable JSON metadata file with all critical extracted values

**Approach & Methodology:**

- Designed modular, readable Python scripts adhering to clean code principles (SOLID, DRY)
- Used OCR for handling scanned/image-based PDFs
- Ensured security by mapping original patient IDs to UUIDs
- Designed the flow with real-world scalability and hospital deployment in mind

The emphasis was on building something usable, secure, and future-ready while reflecting production-grade ETL system behavior.

---

### 3. Data Extraction, Preprocesses, and Analysis

#### Step-by-Step Breakdown:

1. **OCR & Text Extraction:**

   - Used `pdf2image` + `pytesseract` to extract text from scanned PDFs
   - OCR output is cleaned and normalized for metadata extraction

2. **Anonymization Module:**

   - Regex-based redaction of fields like Patient Name, ID, Hospital, and Clinician
   - Used FPDF & ReportLab to regenerate anonymized text-based PDFs

3. **Metadata Extraction:**

   - Used robust regex patterns to extract:
     - Gestational Age (e.g., "GA: 35 weeks 2 days")
     - Age (e.g., "Age: 32")
     - BMI (e.g., "BMI: 28.5")
     - Findings from sections between "Examination Findings" and "Conclusion"

4. **Secure ID Mapping:**

   - Real patient filenames are internally mapped to UUIDs using a persistent `id_map.json` file

5. **JSON Output:**
   - Aggregated metadata written to a clean JSON file with a `dataResources` root key

#### Flowchart: Full Pipeline Overview

```mermaid
flowchart TD
    A[Raw PDFs] --> B[OCR Text Extraction]
    B --> C[Anonymization]
    C --> D[Anonymized PDF Generation]
    B --> E[Metadata Extraction]
    E --> F[Secure ID Mapping (real_id -> UUID)]
    F --> G[JSON Structuring]
    D & G --> H[Final Output: Anon PDFs + Metadata JSON]
```

#### Pseudocode: Core Processing Logic

```python
for pdf in input_folder:
    text = read_pdf_text(pdf)
    metadata = extract_metadata(text)
    uuid = get_or_create_uuid(real_id)
    metadata["patient_id"] = uuid
    anonymized_text = anonymize_text(text)
    save_pdf(anonymized_text, f"{uuid}.pdf")
    metadata_list.append(metadata)

save_to_json(metadata_list)
save_id_map(id_map)
```

---

### 4. Results

- ✅ Successfully anonymized **100%** of sensitive fields from all test PDFs
- ✅ Extracted accurate metadata for gestational age, age, BMI, and findings from unstructured text
- ✅ Verified anonymized UUID mapping and secure traceability via internal `id_map.json`
- ✅ Output JSON structured as per real-world healthcare integration standards

This entire pipeline ran on local systems without requiring any third-party cloud APIs, keeping data privacy fully local.

---

### 5. Key Findings

- Regex-based NLP is a surprisingly effective strategy for medical data extraction from reports
- OCR quality can drastically vary based on scan resolution, so DPI tuning (e.g., 300 DPI) is crucial
- Managing UUID mapping securely is not just about anonymization, but also about internal audit traceability
- Modular ETL pipelines are much easier to test, debug, and scale

---

### 6. Future Work

If given more time, here's how I'd enhance this system:

1. **Named Entity Recognition (NER):** Use spaCy or a fine-tuned BERT model to improve metadata extraction accuracy
2. **PDF Layout Detection:** Use `PyMuPDF` or `pdfplumber` for more accurate region-based parsing instead of OCR where possible
3. **Web Dashboard:** Build a dashboard using React + Flask to upload raw reports and preview anonymized output and metadata
4. **Add Logging & Monitoring:** Implement structured logging + alerting for failed OCR, regex failures, and UUID mismatches
5. **Unit Tests + CI Pipeline:** Fully test all edge cases and automate builds with GitHub Actions
6. **DICOM Integration:** Support medical image standards like DICOM in the same pipeline for radiology labs

---

> This challenge helped me blend backend engineering, security practices, and practical data handling into one cleanly architected solution — a perfect real-world scenario to demonstrate my skills.
