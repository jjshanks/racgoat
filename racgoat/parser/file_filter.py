"""File filtering logic for binary and generated files."""


class FileFilter:
    """Filter for excluding binary and generated files from diff summaries."""

    def __init__(self):
        """Initialize filter with default patterns."""
        self.generated_patterns = ['.lock', '.min.js', '.min.css', '.map', '.bundle.js']
        self.generated_files = ['package-lock.json', 'yarn.lock', 'poetry.lock']
        self.generated_globs = ['*.generated.*']
        self.excluded_dirs = ['dist/', 'build/']

    def is_filtered(self, file_path: str) -> bool:
        """
        Check if a file should be excluded from the summary.

        Args:
            file_path: Path to the file as it appears in the diff

        Returns:
            True if file should be filtered out, False otherwise
        """
        # Check specific filenames (package-lock.json, etc.)
        if any(file_path.endswith(filename) or f'/{filename}' in file_path
               for filename in self.generated_files):
            return True

        # Check extension patterns (.lock, .min.js, etc.)
        if any(file_path.endswith(pattern) for pattern in self.generated_patterns):
            return True

        # Check glob patterns (*.generated.*)
        for glob_pattern in self.generated_globs:
            # Convert *.generated.* to check for .generated. in filename
            if '.generated.' in file_path:
                return True

        # Check directory prefixes (dist/, build/)
        for excluded_dir in self.excluded_dirs:
            if file_path.startswith(excluded_dir) or f'/{excluded_dir}' in file_path:
                return True

        return False
