import json
from pathlib import Path
from typing import Dict

from src.core.exceptions import UUIDMappingException
from src.core.utils import atomic_write_json


class UUIDMappingService:
    """Persist mapping from original IDs to anonymized UUIDs."""

    def __init__(self, mapping_file: str) -> None:
        self._mapping_path = Path(mapping_file)
        self._mapping: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._mapping_path.exists():
            try:
                self._mapping = json.loads(self._mapping_path.read_text())
            except Exception as exc:
                raise UUIDMappingException(str(exc)) from exc

    def get_or_create_uuid(self, original_id: str) -> str:
        if original_id in self._mapping:
            return self._mapping[original_id]
        return self._create_uuid(original_id)

    def _create_uuid(self, original_id: str) -> str:
        import uuid

        new_id = str(uuid.uuid4())
        self._mapping[original_id] = new_id
        self.save()
        return new_id

    def save(self) -> None:
        try:
            atomic_write_json(str(self._mapping_path), self._mapping)
        except Exception as exc:
            raise UUIDMappingException(str(exc)) from exc
