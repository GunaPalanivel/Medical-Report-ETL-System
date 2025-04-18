from pdf2image import convert_from_path
from fpdf import FPDF
import pytesseract
import os

# Poppler path
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"


# path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def write_anonymized_pdf(original_path, output_path, anonymized_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def sanitize(text):
        # Replace em dash and any non-latin1 characters
        return text.encode("latin-1", errors="replace").decode("latin-1")

    for line in anonymized_text.split("\n"):
        sanitized_line = sanitize(line)
        pdf.multi_cell(0, 10, sanitized_line)

    pdf.output(output_path)
    print(f"✅ Saved anonymized report to {output_path}")



def read_pdf_text(pdf_path):
    """
    Extracts text from scanned PDFs using OCR (Tesseract).
    """
    text = ""
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)


    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img)
        text += page_text + "\n"
    
    return text

