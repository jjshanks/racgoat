"""Integration test: Invalid command-line arguments.

Tests Scenario 8 from quickstart.md - displaying usage help for invalid
command-line arguments.
"""

import subprocess
import sys


def test_invalid_arguments_error():
    """Display usage help for invalid command-line arguments.

    Scenario:
    - Given: -o flag without argument
    - When: run CLI
    - Then: stderr contains usage, exit 2 (argparse usage error)
    """
    # Test 1: Missing argument after -o flag
    result = subprocess.run(
        [sys.executable, "-m", "racgoat", "-o"],
        input="",
        text=True,
        capture_output=True,
        timeout=5
    )

    # Should fail with exit code 2 (argparse usage error - Python standard)
    assert result.returncode == 2, f"Expected exit code 2, got {result.returncode}"

    # stderr should contain usage message
    assert "usage:" in result.stderr.lower(), \
        f"Expected 'usage:' in stderr: {result.stderr}"

    # stderr should mention the -o option
    assert "-o" in result.stderr or "--output" in result.stderr, \
        f"Expected '-o' or '--output' in stderr: {result.stderr}"


def test_unknown_flag_error():
    """Display error for unknown command-line flags.

    Scenario:
    - Given: unknown flag like --invalid-flag
    - When: run CLI
    - Then: stderr contains usage and error, exit 2 (argparse usage error)
    """
    result = subprocess.run(
        [sys.executable, "-m", "racgoat", "--invalid-flag"],
        input="",
        text=True,
        capture_output=True,
        timeout=5
    )

    # Should fail with exit code 2 (argparse usage error - Python standard)
    assert result.returncode == 2, f"Expected exit code 2, got {result.returncode}"

    # stderr should contain usage message
    assert "usage:" in result.stderr.lower(), \
        f"Expected 'usage:' in stderr: {result.stderr}"

    # stderr should mention the error
    assert "unrecognized arguments" in result.stderr.lower() or "invalid" in result.stderr.lower(), \
        f"Expected error message in stderr: {result.stderr}"
