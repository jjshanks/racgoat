"""Custom exceptions for RacGoat application.

Even the nimblest raccoon stumbles sometimes, and even the surest-footed goat
can't climb every cliff. These exceptions help us fail gracefully!
"""

from racgoat.constants import MAX_DIFF_LINES


class DiffTooLargeError(Exception):
    """Exception raised when diff exceeds the maximum line limit.

    The raccoon's treasure pile has gotten too big to carry!

    Attributes:
        actual_lines: Actual diff line count
        limit: Maximum allowed lines (MAX_DIFF_LINES)
        message: User-friendly error text with raccoon/goat theme
    """

    def __init__(self, actual_lines: int, limit: int = MAX_DIFF_LINES):
        """Initialize DiffTooLargeError.

        Args:
            actual_lines: Actual line count in the diff
            limit: Maximum allowed lines (default: MAX_DIFF_LINES)
        """
        self.actual_lines = actual_lines
        self.limit = limit
        self.message = (
            f"🦝 This diff is too large! RacGoat can handle up to {limit:,} lines,\n"
            f"but this diff has {actual_lines:,}. Consider reviewing in smaller chunks. 🐐"
        )
        super().__init__(self.message)


class MalformedHunkError(Exception):
    """Exception raised when a hunk fails parsing validation.

    This exception is caught internally by the parser and converted to a
    malformed DiffHunk (is_malformed=True). It should never propagate to
    the UI layer.

    The goat found a rocky patch it can't climb - but it remembers the path!

    Attributes:
        hunk_index: Position in file's hunk list
        raw_hunk: Unparsed hunk text
        reason: Parse failure description
    """

    def __init__(self, hunk_index: int, raw_hunk: str, reason: str):
        """Initialize MalformedHunkError.

        Args:
            hunk_index: Position of hunk in file (0-indexed)
            raw_hunk: Raw unparsed hunk text
            reason: Description of parse failure
                    Examples: "Invalid header format", "Mismatched line count"
        """
        self.hunk_index = hunk_index
        self.raw_hunk = raw_hunk
        self.reason = reason
        message = f"Hunk {hunk_index} failed parsing: {reason}"
        super().__init__(message)
