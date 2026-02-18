from src.features.anonymization import (
    PIIRedactor,
    PIIPatternRegistry,
    build_default_registry,
    RedactionValidator
)


def test_full_anonymization_flow():
    # 1. Setup Registry
    registry = build_default_registry()
    
    # 2. Setup Redactor
    redactor = PIIRedactor(registry.get_all())
    
    # 3. Setup Validator
    validator = RedactionValidator(registry.get_all())
    
    # 4. Sample Text with PII
    sample_text = """
    Patient Name: John Doe
    Patient ID: 12345-XYZ
    Hospital Name: General Hospital
    Clinician: Dr. Smith
    Diagnosis: Normal
    """
    
    # 5. Redact
    redacted_text = redactor.redact(sample_text)
    
    # 6. Validate
    assert "John Doe" not in redacted_text
    assert "12345-XYZ" not in redacted_text
    assert "General Hospital" not in redacted_text
    assert "Dr. Smith" not in redacted_text
    assert "[ANONYMIZED]" in redacted_text
    
    # 7. Check Validator
    is_valid = validator.validate(redacted_text)
    assert is_valid


def test_validator_detects_leakage():
    registry = build_default_registry()
    validator = RedactionValidator(registry.get_all())
    
    leaking_text = "Patient Name: John Doe"
    is_valid = validator.validate(leaking_text)
    
    assert not is_valid
