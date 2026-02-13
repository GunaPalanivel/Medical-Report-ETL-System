from src.features.anonymization import (
    PIIPattern,
    PIIPatternRegistry,
    PIIRedactor,
    RedactionValidator,
    UUIDMappingService,
    build_default_registry,
)


def test_default_registry_has_expected_patterns():
    registry = build_default_registry()
    patterns = registry.get_all()

    assert len(patterns) == 4
    assert [p.name for p in patterns] == [
        "patient_name",
        "patient_id",
        "hospital_name",
        "clinician",
    ]


def test_redactor_replaces_patterns():
    registry = PIIPatternRegistry()
    registry.register(
        PIIPattern(
            name="phone",
            regex=r"\b\d{3}-\d{3}-\d{4}\b",
            replacement="[PHONE REDACTED]",
            priority=10,
        )
    )

    redactor = PIIRedactor(registry.get_all())
    output = redactor.redact("Call 555-123-4567 for results")

    assert output == "Call [PHONE REDACTED] for results"


def test_redaction_validator_detects_remaining_pii():
    registry = build_default_registry()
    validator = RedactionValidator(registry.get_all())

    raw_text = "Patient Name: Jane Doe"
    redacted = PIIRedactor(registry.get_all()).redact(raw_text)

    assert validator.validate(raw_text) is False
    assert validator.validate(redacted) is True


def test_uuid_mapping_service_persists(tmp_path):
    mapping_path = tmp_path / "id_map.json"

    service = UUIDMappingService(str(mapping_path))
    anon_id = service.get_or_create_uuid("patient_01")

    assert anon_id
    assert mapping_path.exists()
    assert "patient_01" in mapping_path.read_text(encoding="utf-8")
