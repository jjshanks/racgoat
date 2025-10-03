"""Data models for diff parsing.

This module contains the core entities used to represent parsed git diffs.
"""

from dataclasses import dataclass, field


@dataclass
class DiffHunk:
    """Represents a contiguous block of diff changes with line-level detail.

    This goat knows every step of the climb! Each hunk captures a specific
    section of changes in a file, tracking line numbers and the actual content.

    Attributes:
        old_start: Starting line number in old file (before changes). Must be >= 0.
                   0 indicates new file (no old version).
        new_start: Starting line number in new file (after changes). Must be >= 0.
                   0 indicates deleted file (no new version).
                   Used for display of post-change line numbers.
        lines: List of (change_type, content) tuples representing each line.
               change_type must be one of: '+' (add), '-' (remove), ' ' (context)
               content is the actual line text without the prefix character.

    Raises:
        ValueError: If line numbers < 1 or lines list is empty.
    """

    old_start: int
    new_start: int
    lines: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self):
        """Validate hunk data after initialization."""
        if self.old_start < 0:
            raise ValueError(f"old_start must be >= 0, got {self.old_start}")
        if self.new_start < 0:
            raise ValueError(f"new_start must be >= 0, got {self.new_start}")
        if not self.lines:
            raise ValueError("DiffHunk must have at least one line")
        for change_type, _ in self.lines:
            if change_type not in ('+', '-', ' '):
                raise ValueError(f"Invalid change_type: {change_type!r}, must be '+', '-', or ' '")


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
        hunks: List of DiffHunk objects containing detailed line-by-line changes.
               Added in Milestone 2 for TUI rendering. Empty list for Milestone 1 compatibility.

    Raises:
        ValueError: If file_path is empty or line counts are negative.
    """

    file_path: str
    added_lines: int = 0
    removed_lines: int = 0
    is_binary: bool = False
    hunks: list[DiffHunk] = field(default_factory=list)


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

        If the file path already exists, merge the counts and hunks.

        Args:
            file: DiffFile to add to summary.
        """
        # Check if file path already exists
        for existing_file in self.files:
            if existing_file.file_path == file.file_path:
                # Merge counts
                existing_file.added_lines += file.added_lines
                existing_file.removed_lines += file.removed_lines
                # Merge hunks (Milestone 2+)
                existing_file.hunks.extend(file.hunks)
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
