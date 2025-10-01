"""Data models for diff parsing.

This module contains the core entities used to represent parsed git diffs.
"""

from dataclasses import dataclass


@dataclass
class DiffFile:
    """Represents a single file in a git diff with its change statistics.

    Attributes:
        file_path: Path to the file as it appears in the diff (from "+++ b/..." line).
                   Must preserve exact path including special characters and spaces.
        added_lines: Count of added lines (lines starting with "+", excluding hunk markers).
                     Must be >= 0.
        removed_lines: Count of removed lines (lines starting with "-", excluding hunk markers).
                       Must be >= 0.
        is_binary: Whether file is marked as binary in diff.
                   Detected from "Binary files ... differ" marker.

    Raises:
        ValueError: If file_path is empty or line counts are negative.
    """

    file_path: str
    added_lines: int = 0
    removed_lines: int = 0
    is_binary: bool = False


@dataclass
class DiffSummary:
    """Aggregates all parsed files and metadata for a single diff.

    Attributes:
        files: All non-filtered files extracted from diff.
               Ordered by appearance in diff.
               Excludes binary and generated files.
    """

    files: list['DiffFile']

    @property
    def is_empty(self) -> bool:
        """Check if diff contains no changes.

        Returns:
            True if no files in summary, False otherwise.
        """
        return len(self.files) == 0

    @property
    def total_files(self) -> int:
        """Get count of files in summary.

        Returns:
            Number of files in the summary.
        """
        return len(self.files)

    def add_file(self, file: 'DiffFile') -> None:
        """Add a file to the summary.

        If the file path already exists, merge the counts.

        Args:
            file: DiffFile to add to summary.
        """
        # Check if file path already exists
        for existing_file in self.files:
            if existing_file.file_path == file.file_path:
                # Merge counts
                existing_file.added_lines += file.added_lines
                existing_file.removed_lines += file.removed_lines
                return

        # New file, add to list
        self.files.append(file)

    def format_output(self) -> str:
        """Generate output text in required format.

        Format: {file_path}: +{added_lines} -{removed_lines}

        Returns:
            Formatted output string with one line per file, ending with newline.
        """
        if not self.files:
            return ""
        return "\n".join(
            f"{f.file_path}: +{f.added_lines} -{f.removed_lines}"
            for f in self.files
        ) + "\n"
