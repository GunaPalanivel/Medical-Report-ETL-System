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
    import uuid
    # Use a unique temporary file name to avoid collisions between processes
    temp_path = f"{path}.{uuid.uuid4()}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)
    # This replace is atomic on POSIX, but on Windows it might fail if destination exists and is open
    # However, standard replace on Windows (Python 3.3+) should be atomic enough for our needs if no one has the file open.
    # The main issue being solved here is multiple writers writing to the SAME temp file.
    os.replace(temp_path, path)


def write_lines(path: str, lines: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")
