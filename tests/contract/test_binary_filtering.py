"""Contract tests for binary file filtering.

Tests verify that binary files (marked with "Binary files ... differ") are
excluded from the output summary, per contracts/cli-interface.md Test 4.
"""

import subprocess
import tempfile
from pathlib import Path


def test_binary_files_excluded():
    """Binary files should be excluded from output (no file created if all filtered)"""
    diff_input = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # Should succeed (exit 0) even though all files filtered
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"

        # No output file should be created (all files filtered)
        assert not output_file.exists(), "Output file should not be created when all files are filtered"


def test_binary_file_excluded_with_text_file():
    """Binary files excluded, text files included in output"""
    diff_input = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,2 @@
 line1
+line2
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists(), "Output file should be created for non-binary files"

        content = output_file.read_text()

        # Binary file should not appear in output
        assert "image.png" not in content, "Binary file should not appear in output"

        # Text file should appear
        assert "src/main.py" in content, "Text file should appear in output"
        assert "+1 -0" in content, "Text file changes should be counted"


def test_multiple_binary_files_excluded():
    """Multiple binary files all excluded"""
    diff_input = """diff --git a/image1.png b/image1.png
Binary files a/image1.png and b/image1.png differ
diff --git a/icon.jpg b/icon.jpg
Binary files a/icon.jpg and b/icon.jpg differ
diff --git a/data.bin b/data.bin
Binary files a/data.bin and b/data.bin differ
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # All files are binary, so no output file
        assert result.returncode == 0
        assert not output_file.exists(), "No output file when all files are binary"


def test_binary_marker_detection():
    """Verify exact binary marker format is detected"""
    # Standard git binary marker format
    diff_input = """diff --git a/file.dat b/file.dat
Binary files a/file.dat and b/file.dat differ
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert not output_file.exists()
