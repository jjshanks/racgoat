"""Integration test for basic diff processing with default output.

Tests quickstart.md Scenario 1: Basic diff with default output file.
"""

import subprocess
import sys
import tempfile
import textwrap
import os
from pathlib import Path


def test_basic_diff_default_output():
    """Process a basic diff with one file and verify default output.

    Given: diff with src/main.py (+3 -1)
    When: run CLI without -o flag
    Then: review.md created with correct format
    """
    # Sample diff with one file
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
     print('hello')
-    return 0
+    return 1
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory to avoid polluting workspace
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Run the CLI
            result = subprocess.run(
                [sys.executable, "-m", "racgoat"],
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

            # Verify content
            content = output_file.read_text()
            assert content == "src/main.py: +3 -1\n", f"Expected 'src/main.py: +3 -1\\n', got '{content}'"

        finally:
            os.chdir(original_cwd)
