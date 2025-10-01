"""Contract tests for output format validation.

Tests verify that the output format matches the pattern specified in
contracts/output-format.md: {path}: +{added} -{removed}
"""

import re
import subprocess
import tempfile
import textwrap
from pathlib import Path


def test_output_format_matches_pattern():
    """Validate output format matches regex: ^[^\n]+: \+\d+ -\d+$"""
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
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        # Should succeed and create file
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert output_file.exists(), "Output file not created"

        # Validate format
        content = output_file.read_text()
        pattern = r'^[^\n]+: \+\d+ -\d+$'

        lines = content.strip().split('\n')
        for line in lines:
            assert re.match(pattern, line), f"Line does not match pattern: {line}"


def test_output_format_special_chars():
    """Validate paths with spaces and special characters are preserved"""
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
@@ -1,1 +1,2 @@
 # init
+__version__ = '1.0'
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
        assert output_file.exists()

        content = output_file.read_text()

        # Verify path with spaces preserved
        assert "path with spaces/file.py" in content, "Path with spaces not preserved"

        # Verify dunder file preserved
        assert "src/__init__.py" in content, "Dunder file path not preserved"


def test_output_format_zero_counts():
    """Validate +0 -0 allowed for new/deleted files"""
    # Test new file (only additions)
    diff_new_file = textwrap.dedent("""\
        diff --git a/new_file.py b/new_file.py
        new file mode 100644
        index 0000000..abcdefg
        --- /dev/null
        +++ b/new_file.py
        @@ -0,0 +1,10 @@
        +def test():
        +    pass
        +
        +def another():
        +    return 1
        +
        +def third():
        +    return 2
        +
        +# Comment
        """)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_new_file,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "+10 -0" in content, "New file should show +10 -0"

    # Test deleted file (only deletions)
    diff_deleted_file = textwrap.dedent("""\
        diff --git a/deleted_file.py b/deleted_file.py
        deleted file mode 100644
        index abcdefg..0000000
        --- a/deleted_file.py
        +++ /dev/null
        @@ -1,5 +0,0 @@
        -def old():
        -    pass
        -
        -def legacy():
        -    return True
        """)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            ["python", "-m", "racgoat", "-o", str(output_file)],
            input=diff_deleted_file,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "+0 -5" in content, "Deleted file should show +0 -5"


def test_output_format_no_leading_zeros():
    """Validate no leading zeros in counts"""
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,6 @@
+line1
+line2
+line3
+line4
+line5
 existing
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
        assert output_file.exists()

        content = output_file.read_text()

        # Should be "+5 -0", not "+05 -00"
        assert re.search(r'\+0\d', content) is None, "Found leading zero in added count"
        assert re.search(r'-0\d', content) is None, "Found leading zero in removed count"
        assert "+5 -0" in content, "Expected +5 -0 format"


def test_output_format_multiple_files():
    """Validate format for multiple files in diff"""
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
-    print('hello')
+    print('world')
diff --git a/tests/test_main.py b/tests/test_main.py
index 1234567..abcdefg 100644
--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,5 +1,2 @@
 def test():
-    assert True
-
-def test_two():
     assert True
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Old
+# New
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
        assert output_file.exists()

        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have 3 files
        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"

        # Each line should match pattern
        pattern = r'^[^\n]+: \+\d+ -\d+$'
        for line in lines:
            assert re.match(pattern, line), f"Line does not match pattern: {line}"

        # Verify specific files present
        assert "src/main.py:" in content
        assert "tests/test_main.py:" in content
        assert "README.md:" in content
