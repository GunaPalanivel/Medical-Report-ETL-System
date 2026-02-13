from pathlib import Path


def validate_file_exists(path: str) -> None:
    if not Path(path).exists():
        raise FileNotFoundError(f"File not found: {path}")


def validate_pdf(path: str) -> None:
    if not path.lower().endswith(".pdf"):
        raise ValueError(f"Expected PDF file: {path}")


def validate_text_not_empty(text: str) -> None:
    if not text or not text.strip():
        raise ValueError("Extracted text is empty")
