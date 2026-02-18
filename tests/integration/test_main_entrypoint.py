"""Tests for main.py entry point — verifies build_pipeline wiring and main() behavior."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import build_pipeline
from src.core import Settings
from src.pipeline import ETLPipeline


def test_build_pipeline_returns_etl_pipeline():
    settings = Settings.load()
    pipeline = build_pipeline(settings)
    assert isinstance(pipeline, ETLPipeline)


def test_build_pipeline_has_four_stages():
    settings = Settings.load()
    pipeline = build_pipeline(settings)
    assert len(pipeline._stages) == 4


def test_build_pipeline_stage_order():
    """Stages must be in order: OCR → Anonymization → Extraction → Output."""
    settings = Settings.load()
    pipeline = build_pipeline(settings)
    stage_names = [s.name for s in pipeline._stages]
    assert stage_names == ["OCR", "Anonymization", "Extraction", "Output"]
