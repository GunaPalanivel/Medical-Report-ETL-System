METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "patient_id": {"type": "string"},
        "gestational_age": {"type": "string"},
        "age": {"type": "integer"},
        "BMI": {"type": "number"},
        "findings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["patient_id"],
}
