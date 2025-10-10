"""Integration test: All files filtered edge case.

Tests Scenario 9 from quickstart.md - handling diff where all files
are filtered (binary or generated).
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_all_files_filtered():
    """Handle diff where all files are filtered.

    Scenario:
    - Given: diff with only package-lock.json and yarn.lock
    - When: run CLI
    - Then: no output file, exit 0
    """
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/yarn.lock b/yarn.lock
index 1234567..abcdefg 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -1,1 +1,2 @@
 dep1
+dep2
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        # Run CLI with diff input
        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # Should succeed with exit code 0 (treated as empty diff)
        assert result.returncode == 0, \
            f"Expected exit code 0, got {result.returncode}\nstderr: {result.stderr}"

        # No output file should be created (all files filtered)
        assert not output_file.exists(), \
            f"Output file should NOT be created when all files are filtered. Content: {output_file.read_text() if output_file.exists() else 'N/A'}"


def test_binary_files_only_filtered():
    """Handle diff with only binary files.

    Scenario:
    - Given: diff with only binary files
    - When: run CLI
    - Then: no output file, exit 0
    """
    diff_input = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
diff --git a/photo.jpg b/photo.jpg
Binary files a/photo.jpg and b/photo.jpg differ
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        # Run CLI with diff input
        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # Should succeed with exit code 0
        assert result.returncode == 0, \
            f"Expected exit code 0, got {result.returncode}\nstderr: {result.stderr}"

        # No output file should be created
        assert not output_file.exists(), \
            "Output file should NOT be created when all files are binary"
