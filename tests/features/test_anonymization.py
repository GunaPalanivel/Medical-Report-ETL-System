import pytest
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


def test_uuid_idempotent_same_input(tmp_path):
    """Same original_id must always return the same UUID."""
    service = UUIDMappingService(str(tmp_path / "map.json"))
    first = service.get_or_create_uuid("patient_X")
    second = service.get_or_create_uuid("patient_X")
    assert first == second


def test_uuid_reloads_from_disk(tmp_path):
    """A new service instance must read the existing mapping file."""
    path = str(tmp_path / "map.json")
    svc1 = UUIDMappingService(path)
    original_uuid = svc1.get_or_create_uuid("patient_A")

    svc2 = UUIDMappingService(path)
    reloaded_uuid = svc2.get_or_create_uuid("patient_A")
    assert reloaded_uuid == original_uuid


def test_uuid_corrupt_file_raises(tmp_path):
    """Corrupt JSON must raise UUIDMappingException, not silently reset."""
    from src.core.exceptions import UUIDMappingException
    mapping_path = tmp_path / "map.json"
    mapping_path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(UUIDMappingException):
        UUIDMappingService(str(mapping_path))


def test_uuid_different_inputs_different_ids(tmp_path):
    """Two different patients must never get the same UUID."""
    service = UUIDMappingService(str(tmp_path / "map.json"))
    id1 = service.get_or_create_uuid("patient_1")
    id2 = service.get_or_create_uuid("patient_2")
    assert id1 != id2


def test_registry_overwrite_replaces_pattern():
    """Re-registering a pattern with the same name must overwrite it."""
    registry = PIIPatternRegistry()
    registry.register(PIIPattern("test", r"old_regex", "OLD"))
    registry.register(PIIPattern("test", r"new_regex", "NEW"))
    patterns = registry.get_all()
    assert len(patterns) == 1
    assert patterns[0].replacement == "NEW"
