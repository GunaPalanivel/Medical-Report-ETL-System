"""Tests for the exception hierarchy — verifies `except ETLException` catches all custom exceptions."""

import pytest

from src.core.exceptions import (
    ETLException,
    OCRException,
    PDFConversionException,
    TextExtractionException,
    AnonymizationException,
    RedactionException,
    UUIDMappingException,
    ExtractionException,
    FieldValidationException,
    OutputException,
    PDFGenerationException,
    JSONSerializationException,
)

ALL_EXCEPTIONS = [
    OCRException,
    PDFConversionException,
    TextExtractionException,
    AnonymizationException,
    RedactionException,
    UUIDMappingException,
    ExtractionException,
    FieldValidationException,
    OutputException,
    PDFGenerationException,
    JSONSerializationException,
]


@pytest.mark.parametrize("exc_class", ALL_EXCEPTIONS, ids=lambda c: c.__name__)
def test_all_exceptions_are_etl_exception_subclasses(exc_class):
    assert issubclass(exc_class, ETLException)
    with pytest.raises(ETLException):
        raise exc_class("test message")


def test_ocr_hierarchy_chain():
    assert issubclass(PDFConversionException, OCRException)
    assert issubclass(TextExtractionException, OCRException)
    assert issubclass(OCRException, ETLException)


def test_anonymization_hierarchy_chain():
    assert issubclass(RedactionException, AnonymizationException)
    assert issubclass(UUIDMappingException, AnonymizationException)
    assert issubclass(AnonymizationException, ETLException)


def test_extraction_hierarchy_chain():
    assert issubclass(FieldValidationException, ExtractionException)
    assert issubclass(ExtractionException, ETLException)


def test_output_hierarchy_chain():
    assert issubclass(PDFGenerationException, OutputException)
    assert issubclass(JSONSerializationException, OutputException)
    assert issubclass(OutputException, ETLException)


def test_message_propagation():
    msg = "detailed error info"
    for exc_class in ALL_EXCEPTIONS:
        exc = exc_class(msg)
        assert str(exc) == msg
