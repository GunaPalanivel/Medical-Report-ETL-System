from src.core.utils import validate_text_not_empty


def validate_ocr_text(text: str) -> None:
    validate_text_not_empty(text)
