"""Unit tests for CLIArguments entity.

Tests validate:
- Default output_file value
- Custom output_file values
- Validation rules for output_file
"""

import pytest
from racgoat.cli.args import parse_arguments
import sys


def test_cli_arguments_default(monkeypatch):
    """Validate default output_file='review.md'."""
    # Mock sys.argv to simulate no arguments
    monkeypatch.setattr(sys, 'argv', ['racgoat'])

    args = parse_arguments()

    assert args.output == 'review.md'


def test_cli_arguments_custom_short_flag(monkeypatch):
    """Validate custom output_file with -o flag."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o', 'custom_summary.txt'])

    args = parse_arguments()

    assert args.output == 'custom_summary.txt'


def test_cli_arguments_custom_long_flag(monkeypatch):
    """Validate custom output_file with --output flag."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '--output', 'my_review.md'])

    args = parse_arguments()

    assert args.output == 'my_review.md'


def test_cli_arguments_custom_with_path(monkeypatch):
    """Validate output_file with directory path."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o', 'output/summary.txt'])

    args = parse_arguments()

    assert args.output == 'output/summary.txt'


def test_cli_arguments_custom_absolute_path(monkeypatch):
    """Validate output_file with absolute path."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o', '/tmp/review.md'])

    args = parse_arguments()

    assert args.output == '/tmp/review.md'


def test_cli_arguments_validation_non_empty(monkeypatch):
    """Validate output_file cannot be empty string."""
    # Empty string should be handled by argparse
    # If -o is provided without argument, argparse will error
    # This test validates that the parser requires an argument

    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o'])

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments()

    # argparse exits with code 2 for invalid arguments
    assert exc_info.value.code == 2


def test_cli_arguments_unknown_flag(monkeypatch):
    """Validate unknown flags cause error."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '--invalid-flag'])

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments()

    assert exc_info.value.code == 2


def test_cli_arguments_help_flag(monkeypatch):
    """Validate --help flag works."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '--help'])

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments()

    # Help exits with code 0
    assert exc_info.value.code == 0


def test_cli_arguments_special_chars_in_filename(monkeypatch):
    """Validate output_file with special characters."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o', 'my review (v2).txt'])

    args = parse_arguments()

    assert args.output == 'my review (v2).txt'


def test_cli_arguments_with_spaces(monkeypatch):
    """Validate output_file with spaces in path."""
    monkeypatch.setattr(sys, 'argv', ['racgoat', '-o', 'path with spaces/file.txt'])

    args = parse_arguments()

    assert args.output == 'path with spaces/file.txt'


def test_cli_arguments_type_is_namespace(monkeypatch):
    """Validate parse_arguments returns argparse.Namespace."""
    import argparse

    monkeypatch.setattr(sys, 'argv', ['racgoat'])

    args = parse_arguments()

    assert isinstance(args, argparse.Namespace)
    assert hasattr(args, 'output')
