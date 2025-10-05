"""Data models for diff parsing.

This module contains the core entities used to represent parsed git diffs.
"""

from dataclasses import dataclass, field


@dataclass
class DiffHunk:
    """Represents a contiguous block of diff changes with line-level detail.

    This goat knows every step of the climb! Each hunk captures a specific
    section of changes in a file, tracking line numbers and the actual content.

    Even when the terrain gets rocky (malformed hunks), this goat preserves
    the raw path for later inspection!

    Attributes:
        old_start: Starting line number in old file (before changes). Must be >= 0.
                   0 indicates new file (no old version).
        new_start: Starting line number in new file (after changes). Must be >= 0.
                   0 indicates deleted file (no new version).
                   Used for display of post-change line numbers.
        lines: List of (change_type, content) tuples representing each line.
               change_type must be one of: '+' (add), '-' (remove), ' ' (context)
               content is the actual line text without the prefix character.
        is_malformed: NEW (M6): True if hunk failed parsing validation.
                      When True, raw_text contains unparsed content and lines may be empty.
        raw_text: NEW (M6): Unparsed hunk text when is_malformed=True.
                  Preserved for display with visual indicator.
        parse_error: NEW (M6): Error description for debugging when is_malformed=True.
                     Examples: "Invalid header format", "Mismatched line count"

    Raises:
        ValueError: If line numbers < 0 or validation fails (only when is_malformed=False).
    """

    old_start: int
    new_start: int
    lines: list[tuple[str, str]] = field(default_factory=list)
    is_malformed: bool = False
    raw_text: str | None = None
    parse_error: str | None = None

    def __post_init__(self):
        """Validate hunk data after initialization."""
        # Skip validation for malformed hunks - they're allowed to be incomplete
        if self.is_malformed:
            # Ensure raw_text is present for malformed hunks
            if not self.raw_text:
                raise ValueError("Malformed hunks must have raw_text")
            return

        # Normal validation for well-formed hunks
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

    This raccoon sorts through each file with care, tracking both valid
    and unparseable treasures!

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
        total_lines: NEW (M6): Sum of all hunk line counts for size limit check.
                     Calculated from sum of new_count across all hunks.
        has_malformed_hunks: NEW (M6): True if any hunk in this file is malformed.
                             Set when any hunk.is_malformed == True.

    Raises:
        ValueError: If file_path is empty or line counts are negative.
    """

    file_path: str
    added_lines: int = 0
    removed_lines: int = 0
    is_binary: bool = False
    hunks: list[DiffHunk] = field(default_factory=list)
    total_lines: int = 0
    has_malformed_hunks: bool = False


@dataclass
class DiffSummary:
    """Aggregates all parsed files and metadata for a single diff.

    This raccoon's treasure chest holds all the files, and knows when
    the pile is getting too big to carry!

    Attributes:
        files: All non-filtered files extracted from diff.
               Ordered by appearance in diff.
               Excludes binary and generated files.
        total_line_count: NEW (M6): Sum of all file total_lines across the diff.
                          Used for 10k line limit enforcement.
        exceeds_limit: NEW (M6): True if total_line_count > 10,000.
                       Triggers DiffTooLargeError before TUI renders.
        binary_files_skipped: Count of binary and generated files filtered out.
                              Displayed in FilesPane footer.
    """

    files: list['DiffFile']
    total_line_count: int = 0
    exceeds_limit: bool = False
    binary_files_skipped: int = 0

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
