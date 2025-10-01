"""Integration test for custom output file via -o flag.

Tests quickstart.md Scenario 2: Custom output with -o flag.
"""

import subprocess
import tempfile
import os
from pathlib import Path


def test_custom_output_file():
    """Process diff with custom output file.

    Given: diff with tests/test_parser.py
    When: run CLI with -o custom_summary.txt
    Then: custom_summary.txt created, review.md NOT created
    """
    # Sample diff with new file
    diff_input = """diff --git a/tests/test_parser.py b/tests/test_parser.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/tests/test_parser.py
@@ -0,0 +1,10 @@
+def test_parse():
+    pass
+
+def test_filter():
+    pass
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Run the CLI with custom output file
            result = subprocess.run(
                ["python", "-m", "racgoat", "-o", "custom_summary.txt"],
                input=diff_input,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Verify exit code
            assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

            # Verify custom output file exists
            custom_file = Path("custom_summary.txt")
            assert custom_file.exists(), "custom_summary.txt should be created"

            # Verify default file NOT created
            default_file = Path("review.md")
            assert not default_file.exists(), "review.md should NOT be created when -o is specified"

            # Verify content
            content = custom_file.read_text()
            assert content == "tests/test_parser.py: +5 -0\n", f"Expected 'tests/test_parser.py: +5 -0\\n', got '{content}'"

        finally:
            os.chdir(original_cwd)
