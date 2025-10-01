"""Integration test for binary file filtering.

Tests quickstart.md Scenario 4: Binary file filtering.
"""

import subprocess
import tempfile
import os
from pathlib import Path


def test_binary_files_filtered():
    """Filter out binary files from summary.

    Given: diff with image.png (binary) + src/main.py
    When: run CLI
    Then: output contains only src/main.py
    """
    # Diff with binary file and text file
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

            # Verify content - binary file excluded, only text file included
            content = output_file.read_text()
            assert content == "src/main.py: +1 -0\n", f"Expected 'src/main.py: +1 -0\\n', got '{content}'"
            assert "image.png" not in content, "Binary file should not appear in output"

        finally:
            os.chdir(original_cwd)
