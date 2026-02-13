import json
import os
from pathlib import Path
from typing import Iterable, List


def get_pdf_files(directory: str) -> List[str]:
    return [
        str(Path(directory) / name)
        for name in os.listdir(directory)
        if name.lower().endswith(".pdf")
    ]


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: str, payload: object) -> None:
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)
    Path(temp_path).replace(path)


def write_lines(path: str, lines: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")
