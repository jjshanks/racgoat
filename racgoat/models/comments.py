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

from racgoat.constants import MAX_COMMENT_LENGTH


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


# ============================================================================
# Milestone 4: Serialization Models
# ============================================================================
# The models below are for serializing comments to Markdown format.
# They are simpler than the UI/storage models above (no UUIDs, timestamps).
# ============================================================================


@dataclass(frozen=True)
class SerializableComment:
    """Base class for serializable comments (Milestone 4).

    These models are used for Markdown serialization and differ from the
    UI/storage Comment models above. They're simpler (no UUIDs, timestamps)
    and optimized for output generation.

    Args:
        text: Comment content (Markdown preserved, 1-MAX_COMMENT_LENGTH chars)
        comment_type: Discriminator for comment type ("line", "range", "file")
        comment_id: Optional unique identifier (e.g., "c1", "c2"), auto-generated during serialization
        status: Comment status (default: "open", options: "open", "addressed", "wontfix")

    Raises:
        ValueError: If text is empty or exceeds MAX_COMMENT_LENGTH characters
    """
    text: str
    comment_type: str  # Literal["line", "range", "file"] but using str for compatibility
    comment_id: str | None = None
    status: str = "open"

    def __post_init__(self):
        """Validate comment text constraints."""
        if not self.text or len(self.text) < 1:
            raise ValueError("Comment text must not be empty (min 1 character)")
        if len(self.text) > MAX_COMMENT_LENGTH:
            raise ValueError(f"Comment text exceeds maximum length ({MAX_COMMENT_LENGTH:,} characters)")


@dataclass(frozen=True)
class LineComment(SerializableComment):
    """Serializable comment attached to a specific line.

    Args:
        text: Comment content
        line_number: Post-change line number (must be >= 1)

    Raises:
        ValueError: If line_number is less than 1
    """
    line_number: int = 0
    comment_type: str = field(default="line", init=False)

    def __post_init__(self):
        """Validate line number and comment text."""
        # Call parent validation
        object.__setattr__(self, 'comment_type', 'line')
        super().__post_init__()
        if self.line_number < 1:
            raise ValueError("Line number must be positive (>= 1)")


@dataclass(frozen=True)
class RangeComment(SerializableComment):
    """Serializable comment spanning multiple consecutive lines.

    Args:
        text: Comment content
        start_line: First line of range (inclusive, >= 1)
        end_line: Last line of range (inclusive, >= start_line)

    Raises:
        ValueError: If start_line < 1 or end_line < start_line
    """
    start_line: int = 0
    end_line: int = 0
    comment_type: str = field(default="range", init=False)

    def __post_init__(self):
        """Validate range bounds and comment text."""
        object.__setattr__(self, 'comment_type', 'range')
        super().__post_init__()
        if self.start_line < 1:
            raise ValueError("Start line must be positive (>= 1)")
        if self.end_line < self.start_line:
            raise ValueError(f"End line ({self.end_line}) must be >= start line ({self.start_line})")


@dataclass(frozen=True)
class FileComment(SerializableComment):
    """Serializable file-level comment.

    Args:
        text: Comment content
    """
    comment_type: str = field(default="file", init=False)

    def __post_init__(self):
        """Set comment type and validate text."""
        object.__setattr__(self, 'comment_type', 'file')
        super().__post_init__()


@dataclass
class FileReview:
    """Container for all comments on a single file.

    Args:
        file_path: Relative path to file (from repository root, forward slashes)
        comments: List of comments for this file (line, range, file-level)

    Raises:
        ValueError: If file_path is empty or exceeds 100 comments
    """
    file_path: str
    comments: list[SerializableComment] = field(default_factory=list)

    def __post_init__(self):
        """Validate file path and comment count."""
        if not self.file_path:
            raise ValueError("File path must not be empty")
        if len(self.comments) > 100:
            raise ValueError(f"File has {len(self.comments)} comments, maximum is 100")


@dataclass
class ReviewSession:
    """Top-level container for an entire review session.

    Args:
        file_reviews: Map of file path → FileReview
        branch_name: Git branch being reviewed (or "Unknown Branch")
        commit_sha: Git commit SHA (or "Unknown SHA")

    Derived Properties:
        total_comment_count: Sum of comments across all files
        has_comments: Whether any comments exist (determines file output)
        review_id: Timestamp-based unique identifier (YYYYMMDD-HHMMSS)
        files_reviewed: Count of files with comments

    Raises:
        ValueError: If total comments across all files exceed 100
    """
    file_reviews: dict[str, FileReview] = field(default_factory=dict)
    branch_name: str = "Unknown Branch"
    commit_sha: str = "Unknown SHA"

    @property
    def total_comment_count(self) -> int:
        """Total number of comments across all files."""
        return sum(len(review.comments) for review in self.file_reviews.values())

    @property
    def has_comments(self) -> bool:
        """Whether any comments exist in the session."""
        return self.total_comment_count > 0

    @property
    def review_id(self) -> str:
        """Generate timestamp-based unique review ID.

        Returns:
            Review ID in format YYYYMMDD-HHMMSS (e.g., "20250104-143022")
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    @property
    def files_reviewed(self) -> int:
        """Count of files with comments.

        Returns:
            Number of files in file_reviews dictionary
        """
        return len(self.file_reviews)

    def __post_init__(self):
        """Validate total comment count."""
        if self.total_comment_count > 100:
            raise ValueError(f"Session has {self.total_comment_count} comments, maximum is 100")
