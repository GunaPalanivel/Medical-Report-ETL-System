import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .env_loader import load_env_file, apply_env


@dataclass(frozen=True)
class Settings:
    tesseract_path: str
    poppler_path: str
    ocr_dpi: int
    ocr_language: str
    input_dir: str
    output_dir: str
    json_output: str
    id_map_file: str
    log_level: str
    log_file: str

    @classmethod
    def load(cls, env_path: Optional[str] = None) -> "Settings":
        if env_path:
            apply_env(load_env_file(env_path))
        elif Path(".env").exists():
            apply_env(load_env_file(".env"))

        base_dir = Path(os.getcwd())
        data_dir = base_dir / "data"

        return cls(
            tesseract_path=os.getenv("TESSERACT_PATH", r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"),
            poppler_path=os.getenv("POPPLER_PATH", r"C:\\poppler-24.08.0\\Library\\bin"),
            ocr_dpi=int(os.getenv("OCR_DPI", "300")),
            ocr_language=os.getenv("OCR_LANGUAGE", "eng"),
            input_dir=os.getenv("INPUT_DIR", str(data_dir / "raw_reports")),
            output_dir=os.getenv("OUTPUT_DIR", str(data_dir / "anonymized_reports")),
            json_output=os.getenv("JSON_OUTPUT", str(data_dir / "patient_metadata.json")),
            id_map_file=os.getenv("ID_MAP_FILE", str(data_dir / "id_map.json")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", str(base_dir / "logs" / "pipeline.log")),
        )
