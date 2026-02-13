from typing import List

from pdf2image import convert_from_path
from PIL import Image

from src.core.exceptions import PDFConversionException


class PDFConverter:
    """Convert PDF pages to images for OCR."""

    def __init__(self, poppler_path: str) -> None:
        self.poppler_path = poppler_path or None

    def convert(self, pdf_path: str, dpi: int) -> List[Image.Image]:
        try:
            return convert_from_path(pdf_path, dpi=dpi, poppler_path=self.poppler_path)
        except Exception as exc:
            raise PDFConversionException(str(exc)) from exc
