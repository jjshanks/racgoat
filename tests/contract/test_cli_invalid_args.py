"""Contract test: CLI handles invalid arguments with proper error messages.

Test from contracts/cli-interface.md Test 7.
"""

import subprocess
from pathlib import Path


def test_cli_rejects_missing_output_argument():
    """Given: -o flag without argument
    When: run cli
    Then: stderr contains usage, exit code 2 (argparse usage error)
    """
    # Run CLI with -o flag but no argument
    result = subprocess.run(
        ["python", "-m", "racgoat", "-o"],
        input="",
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
        timeout=5,
    )

    # Verify exit code 2 (argparse usage error - Python standard)
    assert result.returncode == 2, f"Expected exit code 2, got {result.returncode}"

    # Verify stderr contains usage information
    assert "usage:" in result.stderr.lower() or "error:" in result.stderr.lower(), \
        f"Expected usage/error message in stderr, got: {result.stderr}"

    # Verify error mentions the -o/--output argument
    assert "-o" in result.stderr or "--output" in result.stderr, \
        f"Expected -o/--output in error message, got: {result.stderr}"


def test_cli_rejects_unknown_flag():
    """Given: unknown flag
    When: run cli
    Then: stderr contains usage/error, exit code 2 (argparse usage error)
    """
    # Run CLI with unknown flag
    result = subprocess.run(
        ["python", "-m", "racgoat", "--invalid-flag"],
        input="",
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
        timeout=5,
    )

    # Verify exit code 2 (argparse usage error - Python standard)
    assert result.returncode == 2, f"Expected exit code 2, got {result.returncode}"

    # Verify stderr contains error information
    assert "usage:" in result.stderr.lower() or "error:" in result.stderr.lower(), \
        f"Expected usage/error message in stderr, got: {result.stderr}"

    # Verify error mentions the invalid flag
    assert "invalid" in result.stderr.lower() or "unrecognized" in result.stderr.lower(), \
        f"Expected 'invalid' or 'unrecognized' in error message, got: {result.stderr}"


def test_cli_rejects_multiple_invalid_flags():
    """Given: multiple unknown flags
    When: run cli
    Then: stderr contains usage/error, exit code 2 (argparse usage error)
    """
    # Run CLI with multiple unknown flags
    result = subprocess.run(
        ["python", "-m", "racgoat", "--foo", "--bar"],
        input="",
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
        timeout=5,
    )

    # Verify exit code 2 (argparse usage error - Python standard)
    assert result.returncode == 2, f"Expected exit code 2, got {result.returncode}"

    # Verify stderr contains error information
    assert "usage:" in result.stderr.lower() or "error:" in result.stderr.lower(), \
        f"Expected usage/error message in stderr, got: {result.stderr}"
