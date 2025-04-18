import re
import os

from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def anonymize_text(text):
    text = re.sub(r"Patient Name[:\s]+[\w\s]+", "Patient Name: [ANONYMIZED]", text)
    text = re.sub(r"Patient ID[:\s]+\w+", "Patient ID: [ANONYMIZED]", text)
    text = re.sub(r"Hospital Name[:\s]+[\w\s]+", "Hospital Name: [ANONYMIZED]", text)
    text = re.sub(r"Clinician[:\s]+[\w\s]+", "Clinician: [ANONYMIZED]", text)
    return text


def write_anonymized_pdf(input_pdf_path, output_pdf_path):
    """
    Reads a PDF file, anonymizes its content, and writes it to a new anonymized PDF file.
    """
    # Read original PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        original_text = page.extract_text()
        if not original_text:
            continue  # Skip empty or image-based pages

        # Anonymize the content
        cleaned_text = anonymize_text(original_text)

        # Write the anonymized text back to a new PDF page
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        text_object = can.beginText(40, 750)  # Start position
        for line in cleaned_text.split("\n"):
            text_object.textLine(line)
        can.drawText(text_object)
        can.save()

        # Move to beginning of BytesIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)
        writer.add_page(new_pdf.pages[0])

    # Save to output path
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
