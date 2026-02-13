import pytesseract
from PIL import Image

from src.core.exceptions import TextExtractionException


class TextExtractor:
    """Extract text from images using Tesseract."""

    def __init__(self, tesseract_path: str, language: str) -> None:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.language = language

    def extract(self, image: Image.Image) -> str:
        try:
            return pytesseract.image_to_string(image, lang=self.language)
        except Exception as exc:
            raise TextExtractionException(str(exc)) from exc
