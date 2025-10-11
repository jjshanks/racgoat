"""Unit tests for diff parser line counting logic.

Tests validate:
- File path extraction from diff headers
- Hunk header parsing
- Added line counting (lines starting with +)
- Removed line counting (lines starting with -)
- Ignoring hunk markers and metadata
- Multi-file diff parsing
"""

import pytest
from racgoat.parser.diff_parser import (
    parse_diff,
    parse_file_header,
    parse_hunk_header,
    is_binary_marker,
)


def test_parse_file_header():
    """Test extraction of file path from '+++ b/...' line."""
    # Standard file header
    line = "+++ b/src/main.py"
    path = parse_file_header(line)
    assert path == "src/main.py"

    # Nested path
    line = "+++ b/src/parser/diff_parser.py"
    path = parse_file_header(line)
    assert path == "src/parser/diff_parser.py"

    # Path with spaces
    line = "+++ b/path with spaces/file.py"
    path = parse_file_header(line)
    assert path == "path with spaces/file.py"

    # Root level file
    line = "+++ b/README.md"
    path = parse_file_header(line)
    assert path == "README.md"


def test_parse_file_header_old_format():
    """Test extraction from '--- a/...' line (should return None or be ignored)."""
    line = "--- a/src/main.py"
    # Old file line should be ignored (we use new file path)
    path = parse_file_header(line)
    assert path is None


def test_parse_hunk_header():
    """Test extraction of line counts from '@@ -X,Y +A,B @@'."""
    # Standard hunk header
    line = "@@ -1,3 +1,5 @@"
    old_start, old_count, new_start, new_count = parse_hunk_header(line)
    assert old_start == 1
    assert old_count == 3
    assert new_start == 1
    assert new_count == 5

    # Different counts
    line = "@@ -10,20 +15,25 @@ def function():"
    old_start, old_count, new_start, new_count = parse_hunk_header(line)
    assert old_start == 10
    assert old_count == 20
    assert new_start == 15
    assert new_count == 25

    # Single line change
    line = "@@ -42,1 +42,1 @@"
    old_start, old_count, new_start, new_count = parse_hunk_header(line)
    assert old_start == 42
    assert old_count == 1
    assert new_start == 42
    assert new_count == 1


def test_is_binary_marker():
    """Test detection of binary file markers."""
    # Binary marker
    line = "Binary files a/image.png and b/image.png differ"
    assert is_binary_marker(line) is True

    # Variations
    line = "Binary files differ"
    assert is_binary_marker(line) is True

    # Not binary markers
    assert is_binary_marker("+++ b/file.py") is False
    assert is_binary_marker("@@ -1,1 +1,1 @@") is False
    assert is_binary_marker("+added line") is False


def test_count_added_lines():
    """Test counting lines starting with '+'."""
    diff_content = """\
diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
     print('hello')
-    return 0
+    return 1
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert len(summary.files) == 1
    assert summary.files[0].file_path == "test.py"
    assert summary.files[0].added_lines == 3  # +import sys, +blank line, +return 1


def test_count_removed_lines():
    """Test counting lines starting with '-'."""
    diff_content = """\
diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,5 +1,3 @@
 def main():
-    x = 1
-    y = 2
-    z = 3
     print('hello')
+    return 0
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert len(summary.files) == 1
    assert summary.files[0].removed_lines == 3  # Three removed lines


def test_ignore_hunk_markers():
    """Test not counting '@@ ... @@' lines as changes."""
    diff_content = """\
diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 line1
+line2
@@ -10,1 +11,2 @@
 line10
+line11
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    # Should count only the + lines, not the @@ markers
    assert summary.files[0].added_lines == 2
    assert summary.files[0].removed_lines == 0


def test_parse_multiple_files():
    """Test parsing diff with multiple files."""
    diff_content = """\
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
-    print('hello')
+    print('world')
diff --git a/tests/test_main.py b/tests/test_main.py
--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,5 +1,2 @@
-def test_one():
-    assert True
-
 def test_two():
     assert True
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Old Title
+# New Title
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert len(summary.files) == 3

    # File 1: src/main.py
    assert summary.files[0].file_path == "src/main.py"
    assert summary.files[0].added_lines == 3  # +import sys, +blank, +print('world')
    assert summary.files[0].removed_lines == 1  # -print('hello')

    # File 2: tests/test_main.py
    assert summary.files[1].file_path == "tests/test_main.py"
    assert summary.files[1].added_lines == 0
    assert summary.files[1].removed_lines == 3

    # File 3: README.md
    assert summary.files[2].file_path == "README.md"
    assert summary.files[2].added_lines == 1
    assert summary.files[2].removed_lines == 1


def test_parse_empty_diff():
    """Test parsing empty diff returns empty summary."""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff([])
    assert summary.is_empty is True
    assert len(summary.files) == 0


def test_parse_diff_with_context_lines():
    """Test that context lines (no prefix) are not counted."""
    diff_content = """\
diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,5 +1,6 @@
 line1
 line2
+added_line
 line3
 line4
-removed_line
 line5
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert summary.files[0].added_lines == 1
    assert summary.files[0].removed_lines == 1
    # Context lines (line1-5) should not be counted


def test_parse_file_header_special_chars():
    """Test file paths with special characters."""
    line = "+++ b/path/with/__init__.py"
    path = parse_file_header(line)
    assert path == "path/with/__init__.py"

    line = "+++ b/tests/test_@decorator.py"
    path = parse_file_header(line)
    assert path == "tests/test_@decorator.py"


def test_parse_new_file():
    """Test parsing diff for a new file."""
    diff_content = """\
diff --git a/new_file.py b/new_file.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,5 @@
+def new_function():
+    pass
+
+def another_function():
+    return True
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert len(summary.files) == 1
    assert summary.files[0].file_path == "new_file.py"
    assert summary.files[0].added_lines == 5
    assert summary.files[0].removed_lines == 0


def test_parse_deleted_file():
    """Test parsing diff for a deleted file."""
    diff_content = """\
diff --git a/old_file.py b/old_file.py
deleted file mode 100644
index abcdefg..0000000
--- a/old_file.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_function():
-    pass
-
"""
    from racgoat.parser.models import DiffSummary

    summary = parse_diff(list(diff_content.splitlines()))

    assert len(summary.files) == 1
    assert summary.files[0].file_path == "old_file.py"
    assert summary.files[0].added_lines == 0
    assert summary.files[0].removed_lines == 3
