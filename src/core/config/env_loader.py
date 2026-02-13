import os
from pathlib import Path
from typing import Dict


def load_env_file(path: str) -> Dict[str, str]:
    """Load simple KEY=VALUE pairs from a .env file."""
    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: Dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"')

    return values


def apply_env(values: Dict[str, str]) -> None:
    """Apply env values only when not already set in the environment."""
    for key, value in values.items():
        if key not in os.environ:
            os.environ[key] = value
