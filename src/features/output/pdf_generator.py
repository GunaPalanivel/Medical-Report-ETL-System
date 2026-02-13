from fpdf import FPDF

from src.core.exceptions import PDFGenerationException


class PDFGenerator:
    """Generate anonymized PDFs from text."""

    def generate(self, anonymized_text: str, output_path: str) -> None:
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            def sanitize(text: str) -> str:
                return text.encode("latin-1", errors="replace").decode("latin-1")

            for line in anonymized_text.split("\n"):
                pdf.multi_cell(0, 10, sanitize(line))

            pdf.output(output_path)
        except Exception as exc:
            raise PDFGenerationException(str(exc)) from exc
