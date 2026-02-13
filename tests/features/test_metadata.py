from src.features.metadata import (
    AgeExtractor,
    BMIExtractor,
    FindingsExtractor,
    GestationalAgeExtractor,
    MetadataExtractor,
)


_SAMPLE_TEXT = """
Patient ID: 12345
Age: 33
BMI: 28
GA: 24 weeks 3 days
Examination Findings
Head : Normal skull apperance
Brain : No choroid plexus cyst seen
Conclusion
Normal scan
"""


def test_extractors_parse_fields():
    assert AgeExtractor().extract(_SAMPLE_TEXT) == 33
    assert BMIExtractor().extract(_SAMPLE_TEXT) == 28.0
    assert GestationalAgeExtractor().extract(_SAMPLE_TEXT) == "24 weeks 3 days"

    findings = FindingsExtractor().extract(_SAMPLE_TEXT)
    assert findings
    assert "Head : Normal skull apperance" in findings


def test_metadata_extractor_collects_fields():
    extractor = MetadataExtractor(
        [
            GestationalAgeExtractor(),
            AgeExtractor(),
            BMIExtractor(),
            FindingsExtractor(),
        ]
    )

    metadata = extractor.extract_all(_SAMPLE_TEXT)

    assert metadata["age"] == 33
    assert metadata["BMI"] == 28.0
    assert metadata["gestational_age"] == "24 weeks 3 days"
    assert "findings" in metadata
