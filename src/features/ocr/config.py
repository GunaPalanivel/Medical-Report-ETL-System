from dataclasses import dataclass

from src.core.config import Settings


@dataclass(frozen=True)
class OCRConfig:
    tesseract_path: str
    poppler_path: str
    dpi: int
    language: str


def load_ocr_config(settings: Settings) -> OCRConfig:
    return OCRConfig(
        tesseract_path=settings.tesseract_path,
        poppler_path=settings.poppler_path,
        dpi=settings.ocr_dpi,
        language=settings.ocr_language,
    )
