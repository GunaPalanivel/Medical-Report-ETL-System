"""
src package for Medical Report ETL

Modules exposed:
- anonymizer: Redacts personal info from text
- extractor: Extracts key metadata
- json_writer: Saves metadata to JSON
- pdf_handler: Reads PDFs (OCR) and writes anonymized PDFs
"""

from .anonymizer import anonymize_text
from .extractor import extract_metadata
from .json_writer import save_metadata_json
from .pdf_handler import read_pdf_text, write_anonymized_pdf

__all__ = [
    "anonymize_text",
    "extract_metadata",
    "save_metadata_json",
    "read_pdf_text",
    "write_anonymized_pdf",
]
