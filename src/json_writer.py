import warnings

from src.features.output import JSONSerializer


_serializer = JSONSerializer()


def save_metadata_json(metadata_list, output_path):
    """Backward-compatible wrapper for JSON serialization."""
    warnings.warn(
        "save_metadata_json is deprecated; use JSONSerializer from src.features.output",
        DeprecationWarning,
        stacklevel=2,
    )
    _serializer.serialize(metadata_list, output_path)
