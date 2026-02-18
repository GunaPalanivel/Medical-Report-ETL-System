"""PII Security Invariant Tests — validates data privacy compliance.

A failure here means patient data could leak through the anonymization pipeline.
These tests verify redaction completeness across all 4 PII pattern categories.
"""

import pytest

from src.core.exceptions import RedactionException
from src.features.anonymization import (
    PIIPattern,
    PIIPatternRegistry,
    PIIRedactor,
    RedactionValidator,
    build_default_registry,
)


@pytest.fixture
def default_redactor():
    registry = build_default_registry()
    return PIIRedactor(registry.get_all())


@pytest.fixture
def default_validator():
    registry = build_default_registry()
    return RedactionValidator(registry.get_all())


class TestRedactionCompleteness:
    """Verify all 4 PII fields are removed from realistic medical text."""

    def test_patient_name_redacted(self, default_redactor, sample_medical_text):
        result = default_redactor.redact(sample_medical_text)
        assert "Jane Doe" not in result
        assert "[ANONYMIZED]" in result

    def test_patient_id_redacted(self, default_redactor, sample_medical_text):
        result = default_redactor.redact(sample_medical_text)
        assert "PAT-12345" not in result

    def test_hospital_name_redacted(self, default_redactor, sample_medical_text):
        result = default_redactor.redact(sample_medical_text)
        assert "City General Hospital" not in result

    def test_clinician_redacted(self, default_redactor, sample_medical_text):
        result = default_redactor.redact(sample_medical_text)
        assert "Dr. Smith" not in result

    def test_all_four_fields_redacted(self, default_redactor, default_validator,
                                       sample_medical_text):
        redacted = default_redactor.redact(sample_medical_text)
        assert default_validator.validate(redacted) is True

    def test_non_pii_fields_preserved(self, default_redactor, sample_medical_text):
        result = default_redactor.redact(sample_medical_text)
        # Clinical data must survive redaction
        assert "Age:" in result or "age" in result.lower()
        assert "BMI:" in result or "bmi" in result.lower()


class TestRedactorEdgeCases:
    """Verify redactor handles edge cases without crashing."""

    def test_no_patterns_returns_unchanged(self):
        redactor = PIIRedactor([])
        assert redactor.redact("Patient Name: John") == "Patient Name: John"

    def test_no_pii_in_text_unchanged(self, default_redactor):
        clean_text = "No PII content here, just clinical data."
        assert default_redactor.redact(clean_text) == clean_text

    def test_multiple_patterns_all_applied(self, default_redactor):
        text = "Patient Name: Alice\nPatient ID: X99\nHospital Name: MGH\nClinician: Dr. Jones"
        result = default_redactor.redact(text)
        assert "Alice" not in result
        assert "X99" not in result
        assert "MGH" not in result
        assert "Dr. Jones" not in result

    def test_invalid_regex_raises_redaction_exception(self):
        bad_pattern = PIIPattern("bad", r"[invalid(", "REPLACED")
        redactor = PIIRedactor([bad_pattern])
        with pytest.raises(RedactionException):
            redactor.redact("some text")


class TestValidatorEdgeCases:
    """Verify validator catches leakage and handles edge cases."""

    def test_clean_text_passes(self, default_validator):
        assert default_validator.validate("No PII here") is True

    def test_empty_text_passes(self, default_validator):
        assert default_validator.validate("") is True

    def test_partial_redaction_detected(self, default_validator):
        # If redactor misses one field, validator should catch it
        partial = "Patient Name: [ANONYMIZED]\nPatient ID: LEAK-999"
        assert default_validator.validate(partial) is False

    def test_all_four_patterns_checked(self, default_validator):
        for pii_text in [
            "Patient Name: John Doe",
            "Patient ID: ABC123",
            "Hospital Name: Memorial Hospital",
            "Clinician: Dr. Brown",
        ]:
            assert default_validator.validate(pii_text) is False


class TestUUIDPrivacy:
    """Verify UUID mapping never exposes original identifiers."""

    def test_uuid_output_has_no_trace_of_input(self, tmp_path):
        from src.features.anonymization import UUIDMappingService

        service = UUIDMappingService(str(tmp_path / "map.json"))
        original_id = "PATIENT_REAL_NAME_001"
        anon_id = service.get_or_create_uuid(original_id)

        assert original_id not in anon_id
        assert "PATIENT" not in anon_id
        assert "REAL" not in anon_id
