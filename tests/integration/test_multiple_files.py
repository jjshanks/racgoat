"""Integration test: Multiple files with mixed changes.

Tests Scenario 6 from quickstart.md - processing diff with multiple files
showing additions, deletions, and modifications.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_multiple_files_mixed_changes():
    """Process diff with multiple files showing mixed changes.

    Scenario:
    - Given: diff with src/main.py (+4 -2), tests/test_main.py (+0 -6), README.md (+1 -1)
    - When: run CLI
    - Then: output contains all 3 files with correct counts
    """
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,8 @@
+import sys
+import os
+
 def main():
-    print('hello')
-    x = 1
+    print('world')
     return 0
diff --git a/tests/test_main.py b/tests/test_main.py
index 1234567..abcdefg 100644
--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,10 +1,5 @@
 def test_one():
-    assert True
-
-def test_two():
-    assert True
-
-def test_three():
     assert True
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Old Title
+# New Title
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

        # Should succeed
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}\nstderr: {result.stderr}"

        # Output file should exist
        assert output_file.exists(), "Output file should be created"

        # Read and verify content
        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have exactly 3 lines (one per file)
        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}: {lines}"

        # Verify each file's line counts
        assert "src/main.py: +4 -2" in content, f"Expected 'src/main.py: +4 -2' in output: {content}"
        assert "tests/test_main.py: +0 -6" in content, f"Expected 'tests/test_main.py: +0 -6' in output: {content}"
        assert "README.md: +1 -1" in content, f"Expected 'README.md: +1 -1' in output: {content}"

        # Verify files appear in diff order
        assert lines[0] == "src/main.py: +4 -2"
        assert lines[1] == "tests/test_main.py: +0 -6"
        assert lines[2] == "README.md: +1 -1"
