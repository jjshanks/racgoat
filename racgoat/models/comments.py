"""Comment models for the Core Commenting Engine (Milestone 3).

This module contains data models for storing and managing comments on git diffs.
Comments can be attached to single lines, ranges of lines, or entire files.

The raccoon stashes its thoughts, the goat bleats its wisdom.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class CommentType(Enum):
    """Types of comments supported by RacGoat.

    Like a raccoon's trash categories: single can, range of bins, or whole dumpster.
    """
    LINE = "line"  # Single-line comment
    RANGE = "range"  # Range comment (multiple lines)
    FILE = "file"  # File-level comment


@dataclass
class CommentTarget:
    """Identifies what a comment is attached to (line, range, or file).

    The target is like a treasure map for the raccoon - it shows exactly where
    the shiny comment is hidden.

    Attributes:
        file_path: Path to the file being commented on
        line_number: Specific line number (None for file-level comments)
        line_range: Start and end line numbers for range comments (None for single-line/file)
    """
    file_path: str
    line_number: Optional[int] = None
    line_range: Optional[tuple[int, int]] = None

    def __post_init__(self):
        """Validate target constraints."""
        if not self.file_path:
            raise ValueError("file_path must not be empty")

        # Cannot have both line_number and line_range set
        if self.line_number is not None and self.line_range is not None:
            raise ValueError("Cannot have both line_number and line_range set")

        # Validate range if present
        if self.line_range is not None:
            start, end = self.line_range
            if start > end:
                raise ValueError(f"Invalid range: start ({start}) > end ({end})")

    @property
    def is_line_comment(self) -> bool:
        """True if this is a single-line comment target."""
        return self.line_number is not None

    @property
    def is_range_comment(self) -> bool:
        """True if this is a range comment target."""
        return self.line_range is not None

    @property
    def is_file_comment(self) -> bool:
        """True if this is a file-level comment target."""
        return self.line_number is None and self.line_range is None


@dataclass
class Comment:
    """Represents a piece of user feedback attached to a specific target in the diff.

    Each comment is a precious treasure in the raccoon's cache, stored with care
    and retrieved with precision. The goat guards these wisdoms fiercely.

    Attributes:
        text: The comment content provided by the user
        target: Reference to what this comment is attached to
        comment_type: Enum indicating single-line, range, or file-level
        id: Unique identifier for the comment (UUID, auto-generated)
        timestamp: When the comment was created (auto-generated)
    """
    text: str
    target: CommentTarget
    comment_type: CommentType
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate comment constraints."""
        # Validate target is a CommentTarget instance
        if not isinstance(self.target, CommentTarget):
            raise TypeError("target must be a CommentTarget instance")

        # Note: Text validation happens in CommentStore.add() to allow
        # flexible comment creation for testing/modification scenarios
