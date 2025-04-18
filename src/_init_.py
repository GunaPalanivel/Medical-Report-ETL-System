"""
src package for Medical Report ETL

Modules exposed:
- anonymizer: Redacts personal info from PDFs
- extractor: Extracts key metadata
- json_writer: Converts metadata to JSON
- pdf_handler: Reads/writes PDFs
"""

from .anonymizer import anonymize_text, anonymize_pdf
from .extractor import extract_metadata
from .json_writer import save_to_json
from .pdf_handler import read_pdf_text, write_pdf

__all__ = [
    "anonymize_text",
    "anonymize_pdf",
    "extract_metadata",
    "save_to_json",
    "read_pdf_text",
    "write_pdf"
]
