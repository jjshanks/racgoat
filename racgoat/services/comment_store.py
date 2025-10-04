"""Comment storage service for the Core Commenting Engine (Milestone 3).

This service manages all comments in memory during a review session. It provides
CRUD operations for comments with efficient lookup by file path and line number.

The raccoon's treasure cache - where all the shiny comments are stashed!
"""

from typing import Optional

from racgoat.models.comments import Comment, CommentTarget, CommentType


class CommentStore:
    """Central service for managing all comments in memory.

    Like a raccoon's meticulously organized trash cache - each treasure
    has its place, and the goat knows exactly where to find it!

    Storage structure:
        - Dictionary-based for O(1) lookups
        - Key: (file_path, line_number) or (file_path, None) for file-level
        - Value: list[Comment] to support overlaps
        - Range comments: One entry per line in range

    Capacity: Up to 100 comments per session (enforced limit)
    """

    def __init__(self):
        """Initialize an empty comment store."""
        # Key: (file_path, line_number | None), Value: list[Comment]
        self._comments: dict[tuple[str, Optional[int]], list[Comment]] = {}
        # Track unique comments for capacity (ranges count as one)
        self._unique_comments: dict[str, Comment] = {}

    def add(self, comment: Comment) -> None:
        """Add a new comment to the store.

        Args:
            comment: Comment instance to add

        Raises:
            ValueError: If comment.text is empty
            ValueError: If total comments would exceed 100
            TypeError: If comment is not a Comment instance
        """
        # Validate comment type
        if not isinstance(comment, Comment):
            raise TypeError("comment must be a Comment instance")

        # Validate text is not empty
        if not comment.text or not comment.text.strip():
            raise ValueError("Comment text must not be empty")

        # Check capacity limit (100 unique comments)
        if comment.id not in self._unique_comments and len(self._unique_comments) >= 100:
            raise ValueError("Comment limit reached (100 max)")

        # Add to unique comments tracker
        self._unique_comments[comment.id] = comment

        # Add to storage based on comment type
        if comment.target.is_line_comment:
            # Single-line comment
            key = (comment.target.file_path, comment.target.line_number)
            if key not in self._comments:
                self._comments[key] = []
            self._comments[key].append(comment)

        elif comment.target.is_range_comment:
            # Range comment - store one entry per line
            start, end = comment.target.line_range
            for line_num in range(start, end + 1):
                key = (comment.target.file_path, line_num)
                if key not in self._comments:
                    self._comments[key] = []
                self._comments[key].append(comment)

        elif comment.target.is_file_comment:
            # File-level comment
            key = (comment.target.file_path, None)
            if key not in self._comments:
                self._comments[key] = []
            self._comments[key].append(comment)

    def get(self, file_path: str, line_number: Optional[int]) -> list[Comment]:
        """Retrieve all comments for a specific target.

        Args:
            file_path: Path to the file
            line_number: Line number (None for file-level)

        Returns:
            List of comments (empty if none exist), sorted by timestamp
        """
        key = (file_path, line_number)
        comments = self._comments.get(key, [])
        # Sort by timestamp (oldest first)
        return sorted(comments, key=lambda c: c.timestamp)

    def get_file_comments(self, file_path: str) -> list[Comment]:
        """Get all comments associated with a file (any type).

        Args:
            file_path: Path to the file

        Returns:
            All line, range, and file-level comments for the file,
            sorted by line number (file-level comments first)
        """
        # Collect all unique comments for this file
        unique_comments = {}
        for (f_path, line_num), comments in self._comments.items():
            if f_path == file_path:
                for comment in comments:
                    unique_comments[comment.id] = (line_num, comment)

        # Sort by line number (None first for file-level)
        sorted_comments = sorted(
            unique_comments.values(),
            key=lambda x: (x[0] is not None, x[0] or 0)
        )
        return [c for _, c in sorted_comments]

    def get_comments_for_file(self, file_path: str) -> list[Comment]:
        """Alias for get_file_comments() for contract compatibility.

        Args:
            file_path: Path to the file

        Returns:
            All line, range, and file-level comments for the file,
            sorted by line number (file-level comments first)
        """
        return self.get_file_comments(file_path)

    def update(self, target: CommentTarget | str, new_text: str) -> None:
        """Update the text of an existing comment.

        Args:
            target: Either a CommentTarget or a comment_id (str) to update
            new_text: New comment text

        Raises:
            KeyError: If no comment exists at target or with comment_id
            ValueError: If new_text is empty
            ValueError: If multiple comments exist (ambiguous update)
        """
        if not new_text or not new_text.strip():
            raise ValueError("Comment text must not be empty")

        # Handle update by comment_id (Milestone 5 pattern)
        if isinstance(target, str):
            comment_id = target
            if comment_id not in self._unique_comments:
                raise KeyError(f"No comment with id {comment_id} found")

            comment = self._unique_comments[comment_id]
            comment.text = new_text
            return

        # Handle update by CommentTarget (Milestone 3 pattern)
        # Determine key from target
        if target.is_line_comment:
            key = (target.file_path, target.line_number)
        elif target.is_file_comment:
            key = (target.file_path, None)
        else:
            # Range comment - ambiguous which line to use
            raise ValueError("Cannot update range comment directly (delete + add instead)")

        # Check if comment exists
        if key not in self._comments:
            raise KeyError(f"No comment exists at {target.file_path}:{target.line_number}")

        comments = self._comments[key]
        if len(comments) > 1:
            raise ValueError("Multiple comments exist (ambiguous update - requires comment_id)")

        # Update the comment text (preserve timestamp)
        comment = comments[0]
        comment.text = new_text

    def delete(self, target: CommentTarget | str, comment_id: Optional[str] = None) -> None:
        """Remove a comment from the store.

        Args:
            target: Either a CommentTarget or a comment_id (str) to delete
            comment_id: Optional comment ID (only used when target is CommentTarget)

        Raises:
            KeyError: If no comment exists at target or with comment_id
            ValueError: If multiple comments exist and comment_id is None
            KeyError: If comment_id provided but no matching comment found
        """
        # Handle delete by comment_id alone (Milestone 5 pattern)
        if isinstance(target, str):
            comment_id_to_delete = target
            if comment_id_to_delete not in self._unique_comments:
                raise KeyError(f"No comment with id {comment_id_to_delete} found")

            comment = self._unique_comments[comment_id_to_delete]

            # Remove from all locations based on comment type
            if comment.target.is_range_comment:
                start, end = comment.target.line_range
                for line_num in range(start, end + 1):
                    line_key = (comment.target.file_path, line_num)
                    if line_key in self._comments:
                        self._comments[line_key] = [
                            c for c in self._comments[line_key] if c.id != comment_id_to_delete
                        ]
                        if not self._comments[line_key]:
                            del self._comments[line_key]
            else:
                # Line or file comment
                if comment.target.is_line_comment:
                    key = (comment.target.file_path, comment.target.line_number)
                else:
                    key = (comment.target.file_path, None)

                if key in self._comments:
                    self._comments[key] = [
                        c for c in self._comments[key] if c.id != comment_id_to_delete
                    ]
                    if not self._comments[key]:
                        del self._comments[key]

            # Remove from unique tracker
            del self._unique_comments[comment_id_to_delete]
            return

        # Handle delete by CommentTarget (Milestone 3 pattern)
        # Determine key from target
        if target.is_line_comment:
            key = (target.file_path, target.line_number)
        elif target.is_file_comment:
            key = (target.file_path, None)
        else:
            # Range comment - need to remove from all lines
            if not comment_id:
                raise ValueError("comment_id required for range comment deletion")

            # Find the comment in unique tracker
            if comment_id not in self._unique_comments:
                raise KeyError(f"No comment with id {comment_id} found")

            comment = self._unique_comments[comment_id]
            start, end = comment.target.line_range

            # Remove from all lines in range
            for line_num in range(start, end + 1):
                line_key = (target.file_path, line_num)
                if line_key in self._comments:
                    self._comments[line_key] = [
                        c for c in self._comments[line_key] if c.id != comment_id
                    ]
                    if not self._comments[line_key]:
                        del self._comments[line_key]

            # Remove from unique tracker
            del self._unique_comments[comment_id]
            return

        # Handle line/file comment deletion
        if key not in self._comments:
            raise KeyError(f"No comment exists at {target.file_path}:{target.line_number}")

        comments = self._comments[key]

        if len(comments) > 1 and comment_id is None:
            raise ValueError("Multiple comments exist (ambiguous delete - requires comment_id)")

        # Find and remove the comment
        if comment_id:
            comment_to_remove = None
            for comment in comments:
                if comment.id == comment_id:
                    comment_to_remove = comment
                    break
            if not comment_to_remove:
                raise KeyError(f"No comment with id {comment_id} found at target")
            comments.remove(comment_to_remove)
            del self._unique_comments[comment_id]
        else:
            comment_to_remove = comments[0]
            comments.remove(comment_to_remove)
            del self._unique_comments[comment_to_remove.id]

        # Clean up empty lists
        if not comments:
            del self._comments[key]

    def get_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get a comment by its unique ID.

        Args:
            comment_id: Unique comment ID to retrieve

        Returns:
            Comment instance if found, None if not found
        """
        return self._unique_comments.get(comment_id)

    def has_comment(self, file_path: str, line_number: Optional[int]) -> bool:
        """Check if a comment exists at a specific location.

        Args:
            file_path: Path to the file
            line_number: Line number (None for file-level)

        Returns:
            True if one or more comments exist, False otherwise
        """
        key = (file_path, line_number)
        return key in self._comments and len(self._comments[key]) > 0

    def count(self) -> int:
        """Get total number of unique comments in store.

        Returns:
            Integer between 0 and 100 (inclusive)
            Range comments count as one comment (not one per line)
        """
        return len(self._unique_comments)

    def clear(self) -> None:
        """Remove all comments from the store."""
        self._comments.clear()
        self._unique_comments.clear()

    def get_comment_at_cursor(self, file_path: str, cursor_line: int) -> Optional[Comment]:
        """Get the first comment at cursor position (for edit operations).

        This method supports Milestone 5 edit functionality by finding any comment
        at the cursor position:
        - Line comments: Exact line match
        - Range comments: If cursor is within the range
        - File comments: Returns file comment if no line/range comment found

        Args:
            file_path: Current file being viewed
            cursor_line: Current line number where cursor is positioned (>= 1)

        Returns:
            First comment found at cursor position, or None if no comment exists
            Priority: Line comment > Range comment > File comment
        """
        # Check for line comment first (exact match)
        key = (file_path, cursor_line)
        if key in self._comments and self._comments[key]:
            return self._comments[key][0]

        # Check for file-level comment as fallback
        file_key = (file_path, None)
        if file_key in self._comments and self._comments[file_key]:
            return self._comments[file_key][0]

        return None
