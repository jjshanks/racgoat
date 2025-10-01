"""Integration test: File paths with special characters.

Tests Scenario 7 from quickstart.md - preserving file paths with spaces
and special characters exactly as they appear in the diff.
"""

import subprocess
import tempfile
from pathlib import Path


def test_file_paths_with_special_chars():
    """Preserve file paths with spaces and special characters.

    Scenario:
    - Given: diff with "path with spaces/file.py", "src/__init__.py"
    - When: run CLI
    - Then: paths preserved exactly in output
    """
    diff_input = """diff --git a/path with spaces/file.py b/path with spaces/file.py
index 1234567..abcdefg 100644
--- a/path with spaces/file.py
+++ b/path with spaces/file.py
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/src/__init__.py b/src/__init__.py
index 1234567..abcdefg 100644
--- a/src/__init__.py
+++ b/src/__init__.py
@@ -1,1 +1,3 @@
 # init
+
+__version__ = '1.0'
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        # Run CLI with diff input
        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # Should succeed
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}\nstderr: {result.stderr}"

        # Output file should exist
        assert output_file.exists(), "Output file should be created"

        # Read and verify content
        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have exactly 2 lines
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}: {lines}"

        # Verify paths are preserved exactly
        assert "path with spaces/file.py: +1 -0" in content, \
            f"Expected 'path with spaces/file.py: +1 -0' in output: {content}"
        assert "src/__init__.py: +2 -0" in content, \
            f"Expected 'src/__init__.py: +2 -0' in output: {content}"

        # Verify exact line content
        assert lines[0] == "path with spaces/file.py: +1 -0"
        assert lines[1] == "src/__init__.py: +2 -0"
