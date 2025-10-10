"""Contract tests for mixed file filtering.

Tests verify that when a diff contains both filtered (binary/generated) and
non-filtered files, only the non-filtered files appear in the output, per
contracts/cli-interface.md Test 6.
"""

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def test_mixed_files_filters_correctly():
    """Source file included, generated file excluded in mixed diff"""
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 dep1
+dep2
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists(), "Output file should be created for non-filtered files"

        content = output_file.read_text()

        # Source file should appear
        assert "src/main.py" in content, "Source file should appear in output"
        assert "+1 -0" in content, "Source file changes should be counted"

        # Generated file should NOT appear
        assert "package-lock.json" not in content, "Generated file should not appear in output"


def test_source_and_binary_mixed():
    """Source file included, binary file excluded"""
    diff_input = textwrap.dedent("""\
        diff --git a/src/utils.py b/src/utils.py
        index 1234567..abcdefg 100644
        --- a/src/utils.py
        +++ b/src/utils.py
        @@ -1,1 +1,3 @@
         def util():
        +    pass
        +    return True
        diff --git a/image.png b/image.png
        Binary files a/image.png and b/image.png differ
        """)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()

        # Source file should appear
        assert "src/utils.py" in content
        assert "+2 -0" in content

        # Binary file should NOT appear
        assert "image.png" not in content


def test_multiple_source_with_generated():
    """Multiple source files included, generated files excluded"""
    diff_input = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,3 @@
 import sys
+import os
diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,10 @@
 deps
+more deps
diff --git a/tests/test_main.py b/tests/test_main.py
index 1234567..abcdefg 100644
--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,1 +1,5 @@
 def test():
+    pass
+
+def test_two():
     pass
diff --git a/dist/bundle.min.js b/dist/bundle.min.js
index 1234567..abcdefg 100644
--- a/dist/bundle.min.js
+++ b/dist/bundle.min.js
@@ -1,1 +1,2 @@
 code
+more
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have exactly 2 source files
        assert len(lines) == 2, f"Expected 2 files, got {len(lines)}"

        # Source files should appear
        assert "src/main.py" in content
        assert "tests/test_main.py" in content

        # Generated files should NOT appear
        assert "package-lock.json" not in content
        assert "dist/bundle.min.js" not in content


def test_all_filtered_types_mixed_with_source():
    """Source file with binary, lockfile, minified, and dist files"""
    diff_input = textwrap.dedent("""\
        diff --git a/src/parser.py b/src/parser.py
        index 1234567..abcdefg 100644
        --- a/src/parser.py
        +++ b/src/parser.py
        @@ -1,1 +1,2 @@
         def parse():
        +    return {}
        diff --git a/image.jpg b/image.jpg
        Binary files a/image.jpg and b/image.jpg differ
        diff --git a/yarn.lock b/yarn.lock
        index 1234567..abcdefg 100644
        --- a/yarn.lock
        +++ b/yarn.lock
        @@ -1,1 +1,2 @@
         dep
        +dep2
        diff --git a/app.min.js b/app.min.js
        index 1234567..abcdefg 100644
        --- a/app.min.js
        +++ b/app.min.js
        @@ -1,1 +1,1 @@
        -var a=1;
        +var a=2;
        diff --git a/build/output.txt b/build/output.txt
        index 1234567..abcdefg 100644
        --- a/build/output.txt
        +++ b/build/output.txt
        @@ -1,1 +1,2 @@
         output
        +more
        """)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have exactly 1 source file
        assert len(lines) == 1, f"Expected 1 file, got {len(lines)}"

        # Only source file should appear
        assert "src/parser.py" in content
        assert "+1 -0" in content

        # All filtered files should NOT appear
        assert "image.jpg" not in content
        assert "yarn.lock" not in content
        assert "app.min.js" not in content
        assert "build/output.txt" not in content


def test_file_order_preserved_after_filtering():
    """Files appear in diff order, even after filtering"""
    diff_input = """diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,2 @@
 # Title
+Description
diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 deps
+more
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,2 @@
 code
+more code
diff --git a/dist/bundle.js b/dist/bundle.js
index 1234567..abcdefg 100644
--- a/dist/bundle.js
+++ b/dist/bundle.js
@@ -1,1 +1,2 @@
 bundle
+more
diff --git a/tests/test.py b/tests/test.py
index 1234567..abcdefg 100644
--- a/tests/test.py
+++ b/tests/test.py
@@ -1,1 +1,2 @@
 test
+more test
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have 3 source files
        assert len(lines) == 3

        # Verify order is preserved (README.md, src/main.py, tests/test.py)
        assert lines[0].startswith("README.md:")
        assert lines[1].startswith("src/main.py:")
        assert lines[2].startswith("tests/test.py:")

        # Filtered files should NOT appear
        assert "package-lock.json" not in content
        assert "dist/bundle.js" not in content


def test_single_source_among_many_filtered():
    """Single source file among many filtered files"""
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 dep
+dep2
diff --git a/yarn.lock b/yarn.lock
index 1234567..abcdefg 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -1,1 +1,2 @@
 dep
+dep2
diff --git a/src/utils.py b/src/utils.py
index 1234567..abcdefg 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -1,1 +1,2 @@
 util
+more util
diff --git a/poetry.lock b/poetry.lock
index 1234567..abcdefg 100644
--- a/poetry.lock
+++ b/poetry.lock
@@ -1,1 +1,2 @@
 package
+package2
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        lines = content.strip().split('\n')

        # Should have exactly 1 file
        assert len(lines) == 1

        # Only source file should appear
        assert "src/utils.py: +1 -0" in content

        # No lockfiles should appear
        assert "package-lock.json" not in content
        assert "yarn.lock" not in content
        assert "poetry.lock" not in content
