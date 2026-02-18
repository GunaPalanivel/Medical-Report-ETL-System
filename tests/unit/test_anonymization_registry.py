from src.features.anonymization.pii_patterns import (
    PIIPattern,
    PIIPatternRegistry,
    build_default_registry,
)


def test_pii_pattern_creation():
    pattern = PIIPattern("test", r"test", "REPLACED", priority=1)
    assert pattern.name == "test"
    assert pattern.priority == 1


def test_registry_registration_and_priority():
    registry = PIIPatternRegistry()
    p1 = PIIPattern("p1", "r1", "rep1", priority=10)
    p2 = PIIPattern("p2", "r2", "rep2", priority=5)
    p3 = PIIPattern("p3", "r3", "rep3", priority=20)

    registry.register(p1)
    registry.register(p2)
    registry.register(p3)

    patterns = registry.get_all()
    # Should be sorted by priority (default ascending, but let's check implementation behavior)
    # The implementation uses simple sort, likely ascending integers.
    # p2(5) -> p1(10) -> p3(20)
    assert patterns[0].name == "p2"
    assert patterns[1].name == "p1"
    assert patterns[2].name == "p3"


def test_default_registry():
    registry = build_default_registry()
    patterns = registry.get_all()
    assert len(patterns) >= 4
    names = [p.name for p in patterns]
    assert "patient_name" in names
    assert "patient_id" in names
