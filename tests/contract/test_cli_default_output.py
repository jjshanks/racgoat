"""Contract test: CLI default output file creation.

Tests that the CLI creates the default output file 'review.md' when no -o flag is provided.
Maps to contracts/cli-interface.md Test 1.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_creates_default_output_file(tmp_path):
    """Test that CLI creates review.md by default when processing a diff.

    Given: A diff with one file on stdin
    When: Run CLI without -o flag
    Then: review.md is created with correct format
    """
    # Arrange: Create test diff
    diff_input = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 line1
+line2"""

    # Act: Run CLI in temp directory
    result = subprocess.run(
        [sys.executable, "-m", "racgoat"],
        input=diff_input,
        text=True,
        capture_output=True,
        cwd=tmp_path
    )

    # Assert: Exit code is 0
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

    # Assert: Default output file exists
    output_file = tmp_path / "review.md"
    assert output_file.exists(), "Expected review.md to be created"

    # Assert: Content matches expected format
    content = output_file.read_text()
    expected = "test.py: +1 -0\n"
    assert content == expected, f"Expected '{expected}', got '{content}'"


def test_cli_default_output_multiple_files(tmp_path):
    """Test that default output handles multiple files correctly.

    Given: A diff with multiple files
    When: Run CLI without -o flag
    Then: review.md contains all files in correct format
    """
    # Arrange: Create test diff with multiple files
    diff_input = """diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,3 @@
 line1
+line2
+line3
diff --git a/tests/test.py b/tests/test.py
--- a/tests/test.py
+++ b/tests/test.py
@@ -1,2 +1,1 @@
-removed
 kept"""

    # Act: Run CLI in temp directory
    result = subprocess.run(
        [sys.executable, "-m", "racgoat"],
        input=diff_input,
        text=True,
        capture_output=True,
        cwd=tmp_path
    )

    # Assert: Exit code is 0
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    # Assert: Output file exists
    output_file = tmp_path / "review.md"
    assert output_file.exists(), "Expected review.md to be created"

    # Assert: Content matches expected format
    content = output_file.read_text()
    lines = content.strip().split("\n")
    assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
    assert lines[0] == "src/main.py: +2 -0"
    assert lines[1] == "tests/test.py: +0 -1"
