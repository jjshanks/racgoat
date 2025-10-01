"""Core diff parsing logic."""

import re
from typing import Optional

from racgoat.parser.models import DiffFile, DiffSummary
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
    line_number = 0
    has_diff_header = False
    in_hunk = False

    def save_current_file():
        """Save the current file to summary if not filtered."""
        if current_file_path is not None:
            # Check if file should be filtered
            if current_is_binary or file_filter.is_filtered(current_file_path):
                # Skip this file
                return

            diff_file = DiffFile(
                file_path=current_file_path,
                added_lines=current_added,
                removed_lines=current_removed,
                is_binary=current_is_binary
            )
            summary.add_file(diff_file)

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
                has_diff_header = True
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
                continue

            # Check for hunk header
            if line.startswith("@@"):
                try:
                    # Validate hunk header format
                    parse_hunk_header(line)
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

            # Count added and removed lines
            if line.startswith("+") and not line.startswith("+++"):
                current_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                current_removed += 1
    except ValueError:
        # Re-raise ValueError as-is (already formatted)
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise ValueError(f"Failed to parse diff at line {line_number}: {str(e)}") from e

    # Save last file if exists
    save_current_file()

    return summary
