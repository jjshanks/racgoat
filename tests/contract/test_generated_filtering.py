"""Contract tests for generated file filtering.

Tests verify that generated files (.lock, .min.js, .min.css, .map, .bundle.js,
package-lock.json, yarn.lock, poetry.lock, *.generated.*, dist/, build/) are
excluded from the output summary, per contracts/cli-interface.md Test 5.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_package_lock_json_excluded():
    """package-lock.json should be excluded from output"""
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
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

        # Should succeed (exit 0) even though all files filtered
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"

        # No output file should be created (all files filtered)
        assert not output_file.exists(), "Output file should not be created when all files are filtered"


def test_yarn_lock_excluded():
    """yarn.lock should be excluded from output"""
    diff_input = """diff --git a/yarn.lock b/yarn.lock
index 1234567..abcdefg 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -1,1 +1,2 @@
 dependency1
+dependency2
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
        assert not output_file.exists()


def test_poetry_lock_excluded():
    """poetry.lock should be excluded from output"""
    diff_input = """diff --git a/poetry.lock b/poetry.lock
index 1234567..abcdefg 100644
--- a/poetry.lock
+++ b/poetry.lock
@@ -1,1 +1,2 @@
 [[package]]
+name = "pytest"
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
        assert not output_file.exists()


def test_min_js_excluded():
    """*.min.js files should be excluded from output"""
    diff_input = """diff --git a/app.min.js b/app.min.js
index 1234567..abcdefg 100644
--- a/app.min.js
+++ b/app.min.js
@@ -1,1 +1,1 @@
-var a=1;
+var a=2;
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
        assert not output_file.exists()


def test_min_css_excluded():
    """*.min.css files should be excluded from output"""
    diff_input = """diff --git a/styles.min.css b/styles.min.css
index 1234567..abcdefg 100644
--- a/styles.min.css
+++ b/styles.min.css
@@ -1,1 +1,1 @@
-.a{color:red}
+.a{color:blue}
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
        assert not output_file.exists()


def test_map_files_excluded():
    """*.map files should be excluded from output"""
    diff_input = """diff --git a/bundle.js.map b/bundle.js.map
index 1234567..abcdefg 100644
--- a/bundle.js.map
+++ b/bundle.js.map
@@ -1,1 +1,1 @@
-{"version":3}
+{"version":4}
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
        assert not output_file.exists()


def test_bundle_js_excluded():
    """*.bundle.js files should be excluded from output"""
    diff_input = """diff --git a/main.bundle.js b/main.bundle.js
index 1234567..abcdefg 100644
--- a/main.bundle.js
+++ b/main.bundle.js
@@ -1,1 +1,2 @@
 (function(){})();
+console.log("bundled");
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
        assert not output_file.exists()


def test_generated_pattern_excluded():
    """*.generated.* files should be excluded from output"""
    diff_input = """diff --git a/schema.generated.ts b/schema.generated.ts
index 1234567..abcdefg 100644
--- a/schema.generated.ts
+++ b/schema.generated.ts
@@ -1,1 +1,2 @@
 export interface User {}
+export interface Post {}
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
        assert not output_file.exists()


def test_dist_directory_excluded():
    """Files in dist/ directory should be excluded from output"""
    diff_input = """diff --git a/dist/bundle.js b/dist/bundle.js
index 1234567..abcdefg 100644
--- a/dist/bundle.js
+++ b/dist/bundle.js
@@ -1,1 +1,2 @@
 console.log("hello");
+console.log("world");
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
        assert not output_file.exists()


def test_build_directory_excluded():
    """Files in build/ directory should be excluded from output"""
    diff_input = """diff --git a/build/output.txt b/build/output.txt
index 1234567..abcdefg 100644
--- a/build/output.txt
+++ b/build/output.txt
@@ -1,1 +1,2 @@
 build output
+more output
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
        assert not output_file.exists()


def test_lock_extension_excluded():
    """*.lock files should be excluded from output"""
    diff_input = """diff --git a/Gemfile.lock b/Gemfile.lock
index 1234567..abcdefg 100644
--- a/Gemfile.lock
+++ b/Gemfile.lock
@@ -1,1 +1,2 @@
 GEM
+  remote: https://rubygems.org/
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
        assert not output_file.exists()


def test_multiple_generated_files_excluded():
    """Multiple generated files all excluded"""
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/yarn.lock b/yarn.lock
index 1234567..abcdefg 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -1,1 +1,2 @@
 dep1
+dep2
diff --git a/dist/bundle.min.js b/dist/bundle.min.js
index 1234567..abcdefg 100644
--- a/dist/bundle.min.js
+++ b/dist/bundle.min.js
@@ -1,1 +1,2 @@
 code
+more code
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

        # All files are generated, so no output file
        assert result.returncode == 0
        assert not output_file.exists(), "No output file when all files are generated"


def test_generated_file_excluded_with_source_file():
    """Generated files excluded, source files included in output"""
    diff_input = """diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
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
        output_file = Path(tmpdir) / "review.md"

        result = subprocess.run(
            [sys.executable, "-m", "racgoat", "-o", str(output_file)],
            input=diff_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        assert result.returncode == 0
        assert output_file.exists(), "Output file should be created for source files"

        content = output_file.read_text()

        # Generated file should not appear in output
        assert "package-lock.json" not in content, "Generated file should not appear in output"

        # Source file should appear
        assert "src/utils.py" in content, "Source file should appear in output"
        assert "+2 -0" in content, "Source file changes should be counted"
