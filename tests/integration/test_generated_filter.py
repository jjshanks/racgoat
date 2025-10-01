"""Integration test for generated file filtering.

Tests quickstart.md Scenario 5: Generated file filtering.
"""

import subprocess
import tempfile
import os
from pathlib import Path


def test_generated_files_filtered():
    """Filter out generated files from summary.

    Given: diff with package-lock.json, dist/bundle.min.js, src/utils.py
    When: run CLI
    Then: output contains only src/utils.py
    """
    # Diff with generated files and source file
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/dist/bundle.min.js b/dist/bundle.min.js
index 1234567..abcdefg 100644
--- a/dist/bundle.min.js
+++ b/dist/bundle.min.js
@@ -1,1 +1,2 @@
 code
+more code
diff --git a/src/utils.py b/src/utils.py
index 1234567..abcdefg 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -1,1 +1,3 @@
 def util():
+    pass
+    return True
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Run the CLI
            result = subprocess.run(
                ["python", "-m", "racgoat"],
                input=diff_input,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Verify exit code
            assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

            # Verify output file exists
            output_file = Path("review.md")
            assert output_file.exists(), "review.md should be created"

            # Verify content - generated files excluded, only source file included
            content = output_file.read_text()
            assert content == "src/utils.py: +2 -0\n", f"Expected 'src/utils.py: +2 -0\\n', got '{content}'"
            assert "package-lock.json" not in content, "package-lock.json should not appear in output"
            assert "bundle.min.js" not in content, "bundle.min.js should not appear in output"

        finally:
            os.chdir(original_cwd)
