"""Contract test: CLI custom output file via -o flag.

Tests that the CLI respects the -o flag and creates a custom output file.
Maps to contracts/cli-interface.md Test 2.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_respects_output_flag(tmp_path):
    """Test that CLI creates custom output file when -o flag is provided.

    Given: A diff with one file on stdin
    When: Run CLI with -o custom.txt
    Then: custom.txt is created, review.md is NOT created
    """
    # Arrange: Create test diff
    diff_input = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,2 +1,1 @@
-line1
 line2"""

    # Act: Run CLI with custom output file
    result = subprocess.run(
        [sys.executable, "-m", "racgoat", "-o", "custom.txt"],
        input=diff_input,
        text=True,
        capture_output=True,
        cwd=tmp_path
    )

    # Assert: Exit code is 0
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

    # Assert: Custom output file exists
    custom_file = tmp_path / "custom.txt"
    assert custom_file.exists(), "Expected custom.txt to be created"

    # Assert: Default output file does NOT exist
    default_file = tmp_path / "review.md"
    assert not default_file.exists(), "Expected review.md NOT to be created when -o is used"

    # Assert: Content matches expected format
    content = custom_file.read_text()
    expected = "test.py: +0 -1\n"
    assert content == expected, f"Expected '{expected}', got '{content}'"


def test_cli_custom_output_with_long_flag(tmp_path):
    """Test that CLI respects the --output long flag variant.

    Given: A diff with one file
    When: Run CLI with --output summary.txt
    Then: summary.txt is created with correct content
    """
    # Arrange: Create test diff
    diff_input = """diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,3 @@
 existing
+new1
+new2"""

    # Act: Run CLI with long flag
    result = subprocess.run(
        [sys.executable, "-m", "racgoat", "--output", "summary.txt"],
        input=diff_input,
        text=True,
        capture_output=True,
        cwd=tmp_path
    )

    # Assert: Exit code is 0
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    # Assert: Custom output file exists
    output_file = tmp_path / "summary.txt"
    assert output_file.exists(), "Expected summary.txt to be created"

    # Assert: Content matches expected format
    content = output_file.read_text()
    expected = "src/main.py: +2 -0\n"
    assert content == expected, f"Expected '{expected}', got '{content}'"


def test_cli_custom_output_with_subdirectory(tmp_path):
    """Test that CLI can write to a subdirectory path.

    Given: A diff with one file
    When: Run CLI with -o subdir/output.txt
    Then: subdir/output.txt is created
    """
    # Arrange: Create subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    diff_input = """diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,1 +1,2 @@
 line1
+line2"""

    # Act: Run CLI with subdirectory path
    result = subprocess.run(
        [sys.executable, "-m", "racgoat", "-o", "subdir/output.txt"],
        input=diff_input,
        text=True,
        capture_output=True,
        cwd=tmp_path
    )

    # Assert: Exit code is 0
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    # Assert: Output file exists in subdirectory
    output_file = tmp_path / "subdir" / "output.txt"
    assert output_file.exists(), "Expected subdir/output.txt to be created"

    # Assert: Content is correct
    content = output_file.read_text()
    expected = "file.py: +1 -0\n"
    assert content == expected, f"Expected '{expected}', got '{content}'"
