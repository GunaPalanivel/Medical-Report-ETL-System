from abc import ABC, abstractmethod
from typing import Optional


class BaseExtractor(ABC):
    """Base interface for metadata extractors."""

    @property
    @abstractmethod
    def field_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract(self, text: str) -> Optional[object]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, value: object) -> bool:
        raise NotImplementedError
