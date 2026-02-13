from typing import Dict, Iterable

from src.core.exceptions import ExtractionException

from .extractors import BaseExtractor


class MetadataExtractor:
    """Run all registered extractors and return a metadata dict."""

    def __init__(self, extractors: Iterable[BaseExtractor]) -> None:
        self._extractors = list(extractors)

    def extract_all(self, text: str) -> Dict[str, object]:
        try:
            metadata: Dict[str, object] = {}
            for extractor in self._extractors:
                value = extractor.extract(text)
                if value is None:
                    continue
                if extractor.validate(value):
                    metadata[extractor.field_name] = value
            return metadata
        except Exception as exc:
            raise ExtractionException(str(exc)) from exc
