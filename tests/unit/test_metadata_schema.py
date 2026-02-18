import jsonschema
import pytest
from src.features.metadata.schema import METADATA_SCHEMA


def test_schema_valid_data():
    valid_data = {
        "patient_id": "12345",
        "gestational_age": "20 weeks",
        "age": 30,
        "BMI": 25.5,
        "findings": ["Normal content"],
    }
    jsonschema.validate(instance=valid_data, schema=METADATA_SCHEMA)


def test_schema_missing_required():
    invalid_data = {
        "age": 30
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_data, schema=METADATA_SCHEMA)


def test_schema_invalid_types():
    invalid_data = {
        "patient_id": 12345,  # Should be string
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_data, schema=METADATA_SCHEMA)
