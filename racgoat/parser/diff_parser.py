"""Core diff parsing logic with error handling for Milestone 6."""

import re
from typing import Optional

from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary
from racgoat.parser.file_filter import FileFilter
from racgoat.exceptions import DiffTooLargeError, MalformedHunkError
from racgoat.constants import MAX_DIFF_LINES


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


def parse_hunk_header(line: str, strict: bool = False) -> tuple[int, int, int, int]:
    """Extract line counts from hunk header.

    Args:
        line: Hunk header line (e.g., "@@ -1,3 +1,5 @@")
        strict: If True, require explicit counts (no defaults). For Milestone 6 malformed detection.

    Returns:
        Tuple of (old_start, old_count, new_start, new_count)

    Raises:
        ValueError: If hunk header format is invalid
    """
    # Pattern: @@ -old_start,old_count +new_start,new_count @@
    # Note: count can be omitted if it's 1, e.g., "@@ -0,0 +1 @@" for new files (unless strict=True)
    # MUST have + before new line numbers (strict validation for Milestone 6)
    pattern = r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    match = re.match(pattern, line)

    if match:
        old_start = int(match.group(1))
        old_count_str = match.group(2)
        new_start = int(match.group(3))
        new_count_str = match.group(4)

        # In strict mode, reject if counts are missing
        if strict and (old_count_str is None or new_count_str is None):
            raise ValueError("Invalid header format")

        old_count = int(old_count_str) if old_count_str else 1
        new_count = int(new_count_str) if new_count_str else 1
        return old_start, old_count, new_start, new_count

    # Check for common malformed patterns
    if line.startswith('@@') and '@@' in line[2:]:
        # Has @@ markers but invalid format
        raise ValueError("Invalid header format")

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
                # Skip this file and increment counter
                summary.binary_files_skipped += 1
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


class DiffParser:
    """Modern class-based diff parser with error handling (Milestone 6).

    Supports malformed hunk detection, size limit enforcement, and graceful
    error recovery.
    """

    def __init__(self, size_limit: int = MAX_DIFF_LINES):
        """Initialize parser with optional size limit.

        Args:
            size_limit: Maximum total lines allowed (default: MAX_DIFF_LINES)
        """
        self.size_limit = size_limit
        self.file_filter = FileFilter()

    def parse(self, diff_text: str) -> DiffSummary:
        """Parse git diff with error handling and size limit enforcement.

        Args:
            diff_text: Raw diff text from stdin or file

        Returns:
            DiffSummary with parsed files and metadata

        Raises:
            DiffTooLargeError: If total line count exceeds size_limit
        """
        lines = diff_text.splitlines(keepends=True)
        return self._parse_lines(lines)

    def _parse_lines(self, lines: list[str]) -> DiffSummary:
        """Parse diff lines with malformed hunk detection.

        This method extends the existing parse_diff logic with:
        - Try/catch blocks around hunk parsing
        - Malformed hunk storage (is_malformed=True)
        - Total line count tracking
        - Size limit enforcement

        Args:
            lines: Diff lines to parse

        Returns:
            DiffSummary with all files and line count metadata

        Raises:
            DiffTooLargeError: If total lines > size_limit
        """
        summary = DiffSummary(files=[])
        total_line_count = 0

        current_file_path: Optional[str] = None
        current_added = 0
        current_removed = 0
        current_is_binary = False
        current_hunks: list[DiffHunk] = []
        current_hunk_lines: list[tuple[str, str]] = []
        current_hunk_old_start: Optional[int] = None
        current_hunk_new_start: Optional[int] = None
        current_hunk_old_count: Optional[int] = None
        current_hunk_new_count: Optional[int] = None
        current_hunk_raw_text: list[str] = []  # For malformed hunks
        hunk_index = 0
        line_number = 0
        has_diff_header = False
        in_hunk = False

        def save_current_hunk():
            """Save the current hunk (valid or malformed)."""
            nonlocal current_hunk_lines, current_hunk_old_start, current_hunk_new_start
            nonlocal current_hunk_raw_text, hunk_index, current_hunk_old_count, current_hunk_new_count

            if current_hunk_old_start is not None and current_hunk_new_start is not None:
                # Try to create hunk - may fail validation
                try:
                    if not current_hunk_lines:
                        # No lines but header exists - malformed
                        raise MalformedHunkError(
                            hunk_index,
                            "".join(current_hunk_raw_text),
                            "No content after hunk header"
                        )

                    # Validate line counts match header
                    # Count actual old and new lines
                    actual_old_count = sum(1 for ct, _ in current_hunk_lines if ct in ('-', ' '))
                    actual_new_count = sum(1 for ct, _ in current_hunk_lines if ct in ('+', ' '))

                    # Check if counts match (with tolerance for context lines)
                    # Note: old_count and new_count from header should match actual counts
                    if current_hunk_old_count is not None and actual_old_count != current_hunk_old_count:
                        raise MalformedHunkError(
                            hunk_index,
                            "".join(current_hunk_raw_text),
                            "Mismatched line count"
                        )
                    if current_hunk_new_count is not None and actual_new_count != current_hunk_new_count:
                        raise MalformedHunkError(
                            hunk_index,
                            "".join(current_hunk_raw_text),
                            "Mismatched line count"
                        )

                    hunk = DiffHunk(
                        old_start=current_hunk_old_start,
                        new_start=current_hunk_new_start,
                        lines=current_hunk_lines.copy(),
                    )
                    current_hunks.append(hunk)

                except (ValueError, MalformedHunkError) as e:
                    # Create malformed hunk
                    raw_text = "".join(current_hunk_raw_text)
                    reason = str(e) if isinstance(e, ValueError) else e.reason
                    malformed_hunk = DiffHunk(
                        old_start=current_hunk_old_start or 0,
                        new_start=current_hunk_new_start or 0,
                        lines=[],  # Empty for malformed
                        is_malformed=True,
                        raw_text=raw_text,
                        parse_error=reason
                    )
                    current_hunks.append(malformed_hunk)

                # Reset for next hunk
                current_hunk_lines = []
                current_hunk_old_start = None
                current_hunk_new_start = None
                current_hunk_old_count = None
                current_hunk_new_count = None
                current_hunk_raw_text = []
                hunk_index += 1

        def save_current_file():
            """Save the current file to summary with line count tracking."""
            nonlocal current_hunks, total_line_count

            if current_file_path is not None:
                # Save any pending hunk
                save_current_hunk()

                # Check if file should be filtered
                if current_is_binary or self.file_filter.is_filtered(current_file_path):
                    # Skip this file and increment counter
                    summary.binary_files_skipped += 1
                    current_hunks = []
                    return

                # Calculate total lines for this file
                file_total_lines = current_added  # Use added lines as "new" line count
                has_malformed = any(h.is_malformed for h in current_hunks)

                diff_file = DiffFile(
                    file_path=current_file_path,
                    added_lines=current_added,
                    removed_lines=current_removed,
                    is_binary=current_is_binary,
                    hunks=current_hunks.copy(),
                    total_lines=file_total_lines,
                    has_malformed_hunks=has_malformed
                )
                summary.add_file(diff_file)

                # Update total line count
                total_line_count += file_total_lines

                current_hunks = []

        # Parse all lines
        for line in lines:
            line_number += 1

            # Handle diff header
            if line.startswith("diff --git"):
                save_current_file()
                current_file_path = None
                current_added = 0
                current_removed = 0
                current_is_binary = False
                current_hunks = []
                current_hunk_lines = []
                current_hunk_old_start = None
                current_hunk_new_start = None
                current_hunk_old_count = None
                current_hunk_new_count = None
                current_hunk_raw_text = []
                hunk_index = 0
                has_diff_header = True
                in_hunk = False
                continue

            # Binary marker
            if is_binary_marker(line):
                current_is_binary = True
                continue

            # File header
            file_path = parse_file_header(line)
            if file_path is not None:
                save_current_file()
                current_file_path = file_path if file_path.strip() else None
                current_added = 0
                current_removed = 0
                current_is_binary = False
                current_hunks = []
                current_hunk_lines = []
                current_hunk_old_start = None
                current_hunk_new_start = None
                current_hunk_old_count = None
                current_hunk_new_count = None
                current_hunk_raw_text = []
                hunk_index = 0
                in_hunk = False
                continue

            # Hunk header with malformed detection
            if line.startswith("@@"):
                save_current_hunk()
                try:
                    old_start, old_count, new_start, new_count = parse_hunk_header(line, strict=True)
                    current_hunk_old_start = old_start
                    current_hunk_new_start = new_start
                    current_hunk_old_count = old_count
                    current_hunk_new_count = new_count
                    current_hunk_lines = []
                    current_hunk_raw_text = [line]
                    in_hunk = True
                except ValueError as e:
                    # Malformed hunk header
                    if has_diff_header and current_file_path:
                        # Create malformed hunk immediately
                        malformed_hunk = DiffHunk(
                            old_start=0,
                            new_start=0,
                            lines=[],
                            is_malformed=True,
                            raw_text=line,
                            parse_error="Invalid header format"
                        )
                        current_hunks.append(malformed_hunk)
                        hunk_index += 1
                    in_hunk = False
                continue

            # Track raw text for malformed hunk reconstruction (AFTER checking for new hunk header)
            if in_hunk:
                current_hunk_raw_text.append(line)

            # Count added and removed lines
            if line.startswith("+") and not line.startswith("+++"):
                current_added += 1
                if in_hunk:
                    content = line[1:].rstrip('\n\r')
                    current_hunk_lines.append(('+', content))
            elif line.startswith("-") and not line.startswith("---"):
                current_removed += 1
                if in_hunk:
                    content = line[1:].rstrip('\n\r')
                    current_hunk_lines.append(('-', content))
            elif in_hunk and (line.startswith(" ") or line == '\n'):
                # Context line: either starts with space, or is a blank line (empty context)
                if line == '\n':
                    content = ""  # Empty line
                else:
                    content = line[1:].rstrip('\n\r')
                current_hunk_lines.append((' ', content))

        # Save last file
        save_current_file()

        # Update summary metadata
        summary.total_line_count = total_line_count
        summary.exceeds_limit = total_line_count > self.size_limit

        # Enforce size limit
        if summary.exceeds_limit:
            raise DiffTooLargeError(
                actual_lines=total_line_count,
                limit=self.size_limit
            )

        return summary
