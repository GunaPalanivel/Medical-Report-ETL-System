"""Comprehensive per-extractor tests with boundary values and edge cases.

These tests verify the data contract between raw text and structured JSON output.
Edge cases here cause silent data corruption in downstream JSON.
"""

import pytest

from src.core.exceptions import ExtractionException
from src.features.metadata import (
    AgeExtractor,
    BMIExtractor,
    FindingsExtractor,
    GestationalAgeExtractor,
    MetadataExtractor,
)
from src.features.metadata.validators import validate_age, validate_bmi


# ---------------------------------------------------------------------------
#  AgeExtractor
# ---------------------------------------------------------------------------

class TestAgeExtractor:
    def setup_method(self):
        self.ext = AgeExtractor()

    def test_basic_extraction(self):
        assert self.ext.extract("Age: 30") == 30

    def test_hyphen_separator(self):
        assert self.ext.extract("Age-25") == 25

    def test_colon_no_space(self):
        assert self.ext.extract("Age:45") == 45

    def test_no_match_returns_none(self):
        assert self.ext.extract("No age info here") is None

    def test_field_name(self):
        assert self.ext.field_name == "age"

    @pytest.mark.parametrize("value,expected", [
        (0, True), (60, True), (120, True),
        (-1, False), (121, False), (999, False),
    ])
    def test_validate_boundary(self, value, expected):
        assert self.ext.validate(value) is expected

    def test_validate_rejects_non_int(self):
        assert self.ext.validate("thirty") is False
        assert self.ext.validate(30.5) is False


# ---------------------------------------------------------------------------
#  BMIExtractor
# ---------------------------------------------------------------------------

class TestBMIExtractor:
    def setup_method(self):
        self.ext = BMIExtractor()

    def test_float_extraction(self):
        assert self.ext.extract("BMI: 25.5") == 25.5

    def test_integer_becomes_float(self):
        result = self.ext.extract("BMI: 30")
        assert result == 30.0
        assert isinstance(result, float)

    def test_colon_no_space(self):
        assert self.ext.extract("BMI:22.1") == 22.1

    def test_no_match_returns_none(self):
        assert self.ext.extract("No BMI data") is None

    def test_field_name(self):
        assert self.ext.field_name == "BMI"

    @pytest.mark.parametrize("value,expected", [
        (0.0, True), (25.5, True), (100.0, True),
        (-0.1, False), (100.1, False),
    ])
    def test_validate_boundary(self, value, expected):
        assert self.ext.validate(value) is expected

    def test_validate_rejects_non_float(self):
        assert self.ext.validate("twenty") is False


# ---------------------------------------------------------------------------
#  GestationalAgeExtractor
# ---------------------------------------------------------------------------

class TestGestationalAgeExtractor:
    def setup_method(self):
        self.ext = GestationalAgeExtractor()

    def test_standard_extraction(self):
        result = self.ext.extract("GA: 24 weeks 3 days")
        assert result is not None
        assert "24" in result
        assert "weeks" in result

    def test_no_match_returns_none(self):
        assert self.ext.extract("No gestational info") is None

    def test_field_name(self):
        assert self.ext.field_name == "gestational_age"

    def test_validate_non_empty_string(self):
        assert self.ext.validate("24 weeks 3 days") is True

    def test_validate_empty_string(self):
        assert self.ext.validate("") is False

    def test_validate_non_string(self):
        assert self.ext.validate(24) is False


# ---------------------------------------------------------------------------
#  FindingsExtractor
# ---------------------------------------------------------------------------

class TestFindingsExtractor:
    def setup_method(self):
        self.ext = FindingsExtractor()

    def test_extracts_between_markers(self):
        text = (
            "Examination Findings\n"
            "Head : Normal\n"
            "Brain : Clear\n"
            "Conclusion\n"
            "Normal scan"
        )
        findings = self.ext.extract(text)
        assert findings is not None
        assert len(findings) == 2
        assert "Head : Normal" in findings
        assert "Brain : Clear" in findings

    def test_no_section_returns_none(self):
        assert self.ext.extract("Just plain text") is None

    def test_empty_section_returns_none(self):
        text = "Examination Findings\nConclusion\nDone"
        result = self.ext.extract(text)
        assert result is None

    def test_field_name(self):
        assert self.ext.field_name == "findings"

    def test_validate_list(self):
        assert self.ext.validate(["item1"]) is True
        assert self.ext.validate([]) is True

    def test_validate_rejects_non_list(self):
        assert self.ext.validate("not a list") is False
        assert self.ext.validate(42) is False


# ---------------------------------------------------------------------------
#  MetadataExtractor (orchestrator)
# ---------------------------------------------------------------------------

class TestMetadataExtractor:
    def test_skips_none_values(self):
        """Extractors returning None should not appear in output dict."""
        ext = MetadataExtractor([AgeExtractor(), BMIExtractor()])
        result = ext.extract_all("No extractable data")
        assert result == {}

    def test_skips_invalid_values(self):
        """Values failing validate() should be excluded."""
        # Age of 999 will extract but fail validation (> 120)
        ext = MetadataExtractor([AgeExtractor()])
        result = ext.extract_all("Age: 999")
        assert "age" not in result

    def test_collects_valid_fields(self, sample_medical_text):
        ext = MetadataExtractor([
            AgeExtractor(), BMIExtractor(),
            GestationalAgeExtractor(), FindingsExtractor(),
        ])
        result = ext.extract_all(sample_medical_text)
        assert result["age"] == 33
        assert result["BMI"] == 28.5
        assert "gestational_age" in result
        assert "findings" in result

    def test_wraps_internal_exception(self):
        """Internal errors should become ExtractionException."""
        class _BrokenExtractor:
            field_name = "broken"
            def extract(self, text):
                raise RuntimeError("internal error")
            def validate(self, value):
                return True

        ext = MetadataExtractor([_BrokenExtractor()])
        with pytest.raises(ExtractionException):
            ext.extract_all("any text")


# ---------------------------------------------------------------------------
#  Standalone validators
# ---------------------------------------------------------------------------

class TestStandaloneValidators:
    @pytest.mark.parametrize("val,expected", [
        (0, True), (60, True), (120, True),
        (-1, False), (121, False),
    ])
    def test_validate_age(self, val, expected):
        assert validate_age(val) is expected

    @pytest.mark.parametrize("val,expected", [
        (0.0, True), (25.5, True), (100.0, True),
        (-0.1, False), (100.1, False),
    ])
    def test_validate_bmi(self, val, expected):
        assert validate_bmi(val) is expected
