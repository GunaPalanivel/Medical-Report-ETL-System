"""Tests for src.core.config.env_loader — the first code to run at startup."""

import os
from unittest.mock import patch

from src.core.config.env_loader import load_env_file, apply_env


def test_parses_key_value_pairs(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")

    result = load_env_file(str(env_file))

    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_strips_surrounding_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('MY_PATH="/usr/local/bin"\n')

    result = load_env_file(str(env_file))

    assert result["MY_PATH"] == "/usr/local/bin"


def test_skips_comments_and_blanks(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nKEY=val\n   \n# another\n")

    result = load_env_file(str(env_file))

    assert result == {"KEY": "val"}


def test_missing_file_returns_empty():
    result = load_env_file("/non/existent/.env")
    assert result == {}


def test_lines_without_equals_skipped(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GOOD=value\nBAD_LINE_NO_EQUALS\nALSO_GOOD=yes\n")

    result = load_env_file(str(env_file))

    assert result == {"GOOD": "value", "ALSO_GOOD": "yes"}


def test_apply_env_sets_only_missing():
    with patch.dict(os.environ, {}, clear=True):
        apply_env({"NEW_VAR": "new_value"})
        assert os.environ["NEW_VAR"] == "new_value"


def test_apply_env_preserves_existing():
    with patch.dict(os.environ, {"EXISTING": "original"}, clear=True):
        apply_env({"EXISTING": "overwritten"})
        assert os.environ["EXISTING"] == "original"
