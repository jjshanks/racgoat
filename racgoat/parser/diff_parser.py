"""Core diff parsing logic."""

import re
from typing import Optional

from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary
from racgoat.parser.file_filter import FileFilter


def parse_file_header(line: str) -> Optional[str]:
    """Extract file path from diff file header line.

    Args:
        line: A line from the diff (e.g., "+++ b/path/to/file.py")

    Returns:
        File path if line is a new file header (+++ b/...), None otherwise
    """
    if line.startswith("+++ b/"):
        return line[6:].rstrip('\n\r')  # Remove "+++ b/" prefix and trailing newlines
    return None


def parse_hunk_header(line: str) -> tuple[int, int, int, int]:
    """Extract line counts from hunk header.

    Args:
        line: Hunk header line (e.g., "@@ -1,3 +1,5 @@")

    Returns:
        Tuple of (old_start, old_count, new_start, new_count)

    Raises:
        ValueError: If hunk header format is invalid
    """
    # Pattern: @@ -old_start,old_count +new_start,new_count @@
    # Note: count can be omitted if it's 1, e.g., "@@ -0,0 +1 @@" for new files
    pattern = r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    match = re.match(pattern, line)

    if match:
        old_start = int(match.group(1))
        old_count = int(match.group(2)) if match.group(2) else 1
        new_start = int(match.group(3))
        new_count = int(match.group(4)) if match.group(4) else 1
        return old_start, old_count, new_start, new_count

    raise ValueError(f"Invalid hunk header format: {line}")


def is_binary_marker(line: str) -> bool:
    """Check if line indicates a binary file.

    Args:
        line: A line from the diff

    Returns:
        True if line is a binary file marker, False otherwise
    """
    return line.startswith("Binary files") and "differ" in line


def parse_diff(lines: list[str]) -> DiffSummary:
    """Parse git diff and extract file change statistics.

    Filters out binary files and generated files based on FileFilter rules.

    Args:
        lines: Lines of diff output (from stdin or file)

    Returns:
        DiffSummary containing all non-filtered files with their statistics

    Raises:
        ValueError: If diff format is malformed or corrupted
    """
    summary = DiffSummary(files=[])
    file_filter = FileFilter()

    current_file_path: Optional[str] = None
    current_added = 0
    current_removed = 0
    current_is_binary = False
    current_hunks: list[DiffHunk] = []
    current_hunk_lines: list[tuple[str, str]] = []
    current_hunk_old_start: Optional[int] = None
    current_hunk_new_start: Optional[int] = None
    line_number = 0
    has_diff_header = False
    in_hunk = False

    def save_current_hunk():
        """Save the current hunk if it has content."""
        nonlocal current_hunk_lines, current_hunk_old_start, current_hunk_new_start
        if (
            current_hunk_lines
            and current_hunk_old_start is not None
            and current_hunk_new_start is not None
        ):
            hunk = DiffHunk(
                old_start=current_hunk_old_start,
                new_start=current_hunk_new_start,
                lines=current_hunk_lines.copy(),
            )
            current_hunks.append(hunk)
            current_hunk_lines = []
            current_hunk_old_start = None
            current_hunk_new_start = None

    def save_current_file():
        """Save the current file to summary if not filtered."""
        nonlocal current_hunks
        if current_file_path is not None:
            # Save any pending hunk
            save_current_hunk()

            # Check if file should be filtered
            if current_is_binary or file_filter.is_filtered(current_file_path):
                # Skip this file
                current_hunks = []
                return

            diff_file = DiffFile(
                file_path=current_file_path,
                added_lines=current_added,
                removed_lines=current_removed,
                is_binary=current_is_binary,
                hunks=current_hunks.copy()
            )
            summary.add_file(diff_file)
            current_hunks = []

    try:
        for line in lines:
            line_number += 1

            # Track if we've seen any diff-like headers
            # Also save previous file when starting a new diff
            if line.startswith("diff --git"):
                # Save previous file before starting new one
                save_current_file()
                # Reset for new file
                current_file_path = None
                current_added = 0
                current_removed = 0
                current_is_binary = False
                current_hunks = []
                current_hunk_lines = []
                current_hunk_old_start = None
                current_hunk_new_start = None
                has_diff_header = True
                in_hunk = False
                continue

            # Check for binary file marker
            if is_binary_marker(line):
                current_is_binary = True
                continue

            # Check for file header (new file path)
            file_path = parse_file_header(line)
            if file_path is not None:
                # Save previous file if exists
                save_current_file()

                # Validate file path is not empty
                if not file_path or file_path.strip() == "":
                    raise ValueError(f"Line {line_number}: Empty file path in diff header")

                # Start new file
                current_file_path = file_path
                current_added = 0
                current_removed = 0
                current_is_binary = False
                current_hunks = []
                current_hunk_lines = []
                current_hunk_old_start = None
                current_hunk_new_start = None
                in_hunk = False
                continue

            # Check for hunk header
            if line.startswith("@@"):
                try:
                    # Save previous hunk if exists
                    save_current_hunk()

                    # Parse and store hunk header info
                    old_start, old_count, new_start, new_count = parse_hunk_header(line)
                    current_hunk_old_start = old_start
                    current_hunk_new_start = new_start
                    current_hunk_lines = []
                    in_hunk = True
                except ValueError as e:
                    # Only raise error if we're in a real diff (not just random @@ in output)
                    if has_diff_header and current_file_path:
                        raise ValueError(f"Line {line_number}: {e}")
                continue

            # Check for deleted file (--- a/filename, +++ /dev/null)
            if line.startswith("--- a/") and current_file_path is None:
                # Potential deleted file - need to check next line
                deleted_path = line[6:].rstrip('\n\r')  # Remove "--- a/" and newlines
                if not deleted_path or deleted_path.strip() == "":
                    raise ValueError(f"Line {line_number}: Empty file path in diff header")
                # Store temporarily, will be validated when we see +++ /dev/null
                current_file_path = deleted_path
                continue

            if line.startswith("+++ /dev/null"):
                # Confirmed deleted file - current_file_path already set from --- a/
                # Don't reset current_file_path here
                continue

            # Count added and removed lines, and store in hunk if we're in one
            if line.startswith("+") and not line.startswith("+++"):
                current_added += 1
                if in_hunk:
                    # Store line content without the prefix
                    content = line[1:].rstrip('\n\r')
                    current_hunk_lines.append(('+', content))
            elif line.startswith("-") and not line.startswith("---"):
                current_removed += 1
                if in_hunk:
                    # Store line content without the prefix
                    content = line[1:].rstrip('\n\r')
                    current_hunk_lines.append(('-', content))
            elif in_hunk and line.startswith(" "):
                # Context line (unchanged)
                content = line[1:].rstrip('\n\r')
                current_hunk_lines.append((' ', content))
    except ValueError:
        # Re-raise ValueError as-is (already formatted)
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise ValueError(f"Failed to parse diff at line {line_number}: {str(e)}") from e

    # Save last file if exists
    save_current_file()

    return summary
