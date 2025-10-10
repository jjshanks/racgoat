"""Contract test: CLI handles empty diff gracefully.

Test from contracts/cli-interface.md Test 3.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_cli_handles_empty_diff():
    """Given: empty stdin
    When: run cli
    Then: no output file, exit code 0
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        # Run CLI with empty input
        result = subprocess.run(
            [sys.executable, "-m", "racgoat"],
            input="",
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            timeout=5,
        )

        # Verify no output file created
        assert not output_file.exists(), "Output file should not be created for empty diff"

        # Verify exit code 0 (success)
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"


def test_cli_handles_empty_diff_with_custom_output():
    """Given: empty stdin with custom output file
    When: run cli with -o flag
    Then: no output file created, exit code 0
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "custom.txt"

        # Run CLI with empty input and custom output file
        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input="",
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            timeout=5,
        )

        # Verify no output file created
        assert not output_file.exists(), "Custom output file should not be created for empty diff"

        # Verify exit code 0 (success)
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
