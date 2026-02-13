import warnings

from src.features.metadata import (
    AgeExtractor,
    BMIExtractor,
    FindingsExtractor,
    GestationalAgeExtractor,
    MetadataExtractor,
)


_extractor = MetadataExtractor(
    [
        GestationalAgeExtractor(),
        AgeExtractor(),
        BMIExtractor(),
        FindingsExtractor(),
    ]
)


def extract_metadata(text):
    """Backward-compatible wrapper for metadata extraction."""
    warnings.warn(
        "extract_metadata is deprecated; use MetadataExtractor from src.features.metadata",
        DeprecationWarning,
        stacklevel=2,
    )
    return _extractor.extract_all(text)
