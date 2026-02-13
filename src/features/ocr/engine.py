from src.core.exceptions import OCRException
from src.core.utils import validate_text_not_empty

from .config import OCRConfig
from .pdf_converter import PDFConverter
from .text_extractor import TextExtractor


class OCREngine:
    """Orchestrates PDF to text OCR."""

    def __init__(self, config: OCRConfig) -> None:
        self._converter = PDFConverter(config.poppler_path)
        self._extractor = TextExtractor(config.tesseract_path, config.language)
        self._dpi = config.dpi

    def extract_text(self, pdf_path: str) -> str:
        try:
            images = self._converter.convert(pdf_path, self._dpi)
            text_parts = [self._extractor.extract(image) for image in images]
            text = "\n".join(text_parts)
            validate_text_not_empty(text)
            return text
        except Exception as exc:
            raise OCRException(str(exc)) from exc
