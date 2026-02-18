import json
from pathlib import Path
from typing import Dict

from filelock import FileLock

from src.core.exceptions import UUIDMappingException
from src.core.utils import atomic_write_json


class UUIDMappingService:
    """Persist mapping from original IDs to anonymized UUIDs."""

    def __init__(self, mapping_file: str) -> None:
        self._mapping_path = Path(mapping_file).resolve()
        # Reuse the same lock object to allow re-entrancy on Windows
        self._lock = FileLock(f"{self._mapping_path}.lock")
        self._mapping: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._mapping_path.exists():
            # Use lock to prevent reading while another process is replacing the file
            with self._lock:
                try:
                    self._mapping = json.loads(self._mapping_path.read_text(encoding="utf-8"))
                except Exception as exc:
                    # In case of partial read/write or other issues, try to continue or raise
                    # If the file is empty or corrupted, we might start fresh? 
                    # But failing loudly is safer for data integrity.
                    # However, if concurrent creation happened, it might be fine.
                    # Let's clean up the raise to be more robust?
                    # For now just keep existing behavior but with lock.
                    raise UUIDMappingException(str(exc)) from exc

    def get_or_create_uuid(self, original_id: str) -> str:
        # Check in-memory first for performance
        if original_id in self._mapping:
            return self._mapping[original_id]
            
        # If not found, use a file lock to ensure atomic updates across processes
        with self._lock:
            # Reload mapping to catch updates from other processes
            self._load()
            
            # Check again after reload
            if original_id in self._mapping:
                return self._mapping[original_id]
                
            return self._create_uuid(original_id)

    def __getstate__(self) -> Dict:
        """Exclude lock from pickling."""
        state = self.__dict__.copy()
        if "_lock" in state:
            del state["_lock"]
        return state

    def __setstate__(self, state: Dict) -> None:
        """Restore state and re-initialize lock."""
        self.__dict__.update(state)
        self._lock = FileLock(f"{self._mapping_path}.lock")

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
