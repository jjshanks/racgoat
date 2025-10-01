"""Integration test for empty diff handling.

Tests quickstart.md Scenario 3: Empty diff handling.
"""

import subprocess
import tempfile
import os
from pathlib import Path


def test_empty_diff_no_output():
    """Handle empty diff without creating output file.

    Given: empty stdin
    When: run CLI
    Then: no output file, exit 0
    """
    # Empty input
    diff_input = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Run the CLI with empty input
            result = subprocess.run(
                ["python", "-m", "racgoat"],
                input=diff_input,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Verify exit code is 0 (success)
            assert result.returncode == 0, f"Expected exit code 0 for empty diff, got {result.returncode}. stderr: {result.stderr}"

            # Verify no output file created
            output_file = Path("review.md")
            assert not output_file.exists(), "No output file should be created for empty diff"

        finally:
            os.chdir(original_cwd)
