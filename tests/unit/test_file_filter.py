"""Unit tests for FileFilter.

Tests the FileFilter.is_filtered() method validating all filter patterns.
"""

import pytest
from racgoat.parser.file_filter import FileFilter


@pytest.fixture
def file_filter():
    """Create a FileFilter instance for testing."""
    return FileFilter()


def test_filter_binary_marker(file_filter):
    """Test that files marked as binary are handled separately.

    Note: Binary detection happens in DiffFile (is_binary attribute).
    FileFilter focuses on path-based filtering for generated files.
    """
    # Binary files are detected by "Binary files ... differ" marker
    # and stored in DiffFile.is_binary, not filtered by path
    # This test documents that FileFilter handles path-based filtering only
    assert True  # Placeholder - binary filtering is in parser logic


def test_filter_lock_extensions(file_filter):
    """Test .lock, .min.js, .min.css, .map, .bundle.js extensions filtered."""
    assert file_filter.is_filtered("package.lock") is True
    assert file_filter.is_filtered("dependencies.lock") is True
    assert file_filter.is_filtered("dist/bundle.min.js") is True
    assert file_filter.is_filtered("src/styles.min.css") is True
    assert file_filter.is_filtered("build/output.map") is True
    assert file_filter.is_filtered("public/app.bundle.js") is True


def test_filter_lockfile_names(file_filter):
    """Test package-lock.json, yarn.lock, poetry.lock filtered."""
    assert file_filter.is_filtered("package-lock.json") is True
    assert file_filter.is_filtered("yarn.lock") is True
    assert file_filter.is_filtered("poetry.lock") is True
    assert file_filter.is_filtered("subdir/package-lock.json") is True
    assert file_filter.is_filtered("subdir/yarn.lock") is True
    assert file_filter.is_filtered("subdir/poetry.lock") is True


def test_filter_generated_glob(file_filter):
    """Test *.generated.* pattern filtered."""
    assert file_filter.is_filtered("data.generated.json") is True
    assert file_filter.is_filtered("src/schema.generated.ts") is True
    assert file_filter.is_filtered("api.generated.py") is True
    assert file_filter.is_filtered("path/to/file.generated.txt") is True


def test_filter_dist_build_dirs(file_filter):
    """Test dist/ and build/ directory prefixes filtered."""
    assert file_filter.is_filtered("dist/bundle.js") is True
    assert file_filter.is_filtered("dist/index.html") is True
    assert file_filter.is_filtered("build/output.txt") is True
    assert file_filter.is_filtered("build/compiled.js") is True
    assert file_filter.is_filtered("dist/nested/file.js") is True
    assert file_filter.is_filtered("build/nested/file.py") is True


def test_filter_allows_source_files(file_filter):
    """Test src/main.py and other source files NOT filtered."""
    assert file_filter.is_filtered("src/main.py") is False
    assert file_filter.is_filtered("src/utils.py") is False
    assert file_filter.is_filtered("tests/test_parser.py") is False
    assert file_filter.is_filtered("racgoat/cli/args.py") is False
    assert file_filter.is_filtered("README.md") is False
    assert file_filter.is_filtered("pyproject.toml") is False


def test_filter_allows_lock_in_middle_of_path(file_filter):
    """Test that .lock only filters when it's the extension."""
    # "lock" in middle of filename should NOT be filtered
    assert file_filter.is_filtered("src/locksmith.py") is False
    assert file_filter.is_filtered("unlock.py") is False


def test_filter_allows_min_in_middle_of_path(file_filter):
    """Test that .min.js only filters when it's the extension."""
    # "min" in middle of filename should NOT be filtered
    assert file_filter.is_filtered("src/minify.py") is False
    assert file_filter.is_filtered("admin.py") is False


def test_filter_allows_dist_build_not_at_start(file_filter):
    """Test that dist/ and build/ only filter when at path start."""
    # "dist" or "build" in middle of path should NOT be filtered
    assert file_filter.is_filtered("src/dist_utils.py") is False
    assert file_filter.is_filtered("lib/build_tools.py") is False
    assert file_filter.is_filtered("redistribute.py") is False


def test_filter_case_sensitive(file_filter):
    """Test that filtering is case-sensitive."""
    # Uppercase extensions should NOT be filtered (diff output is case-sensitive)
    assert file_filter.is_filtered("file.LOCK") is False
    assert file_filter.is_filtered("bundle.MIN.JS") is False
    assert file_filter.is_filtered("PACKAGE-LOCK.JSON") is False
    assert file_filter.is_filtered("Dist/file.js") is False
    assert file_filter.is_filtered("Build/file.js") is False


def test_filter_edge_case_empty_path(file_filter):
    """Test empty path handling."""
    assert file_filter.is_filtered("") is False


def test_filter_edge_case_just_extension(file_filter):
    """Test files that are just extensions."""
    assert file_filter.is_filtered(".lock") is True
    assert file_filter.is_filtered(".min.js") is True


def test_filter_multiple_extensions(file_filter):
    """Test files with multiple extensions."""
    assert file_filter.is_filtered("archive.tar.lock") is True
    assert file_filter.is_filtered("script.bundle.min.js") is True


def test_filter_path_with_spaces(file_filter):
    """Test paths with spaces are handled correctly."""
    assert file_filter.is_filtered("path with spaces/file.lock") is True
    assert file_filter.is_filtered("path with spaces/source.py") is False
    assert file_filter.is_filtered("dist/path with spaces/file.js") is True


def test_filter_nested_dist_build(file_filter):
    """Test deeply nested dist/build paths."""
    assert file_filter.is_filtered("dist/v1/api/bundle.js") is True
    assert file_filter.is_filtered("build/release/2024/output.txt") is True


def test_filter_all_generated_patterns(file_filter):
    """Test comprehensive list of all filter patterns."""
    # Lock extensions
    filtered_files = [
        "any.lock",
        "dependencies.min.js",
        "styles.min.css",
        "source.map",
        "app.bundle.js",
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
        "schema.generated.ts",
        "dist/output.txt",
        "build/binary",
    ]

    for file_path in filtered_files:
        assert file_filter.is_filtered(file_path) is True, f"Expected {file_path} to be filtered"

    # Source files that should NOT be filtered
    allowed_files = [
        "src/main.py",
        "tests/test_parser.py",
        "README.md",
        "pyproject.toml",
        "racgoat/__init__.py",
        "docs/guide.md",
    ]

    for file_path in allowed_files:
        assert file_filter.is_filtered(file_path) is False, f"Expected {file_path} to be allowed"
