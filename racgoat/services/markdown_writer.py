"""Markdown serialization service (Milestone 4).

Serializes ReviewSession to Markdown format and writes output files with
atomic operations. Handles file conflicts and write errors gracefully.

The raccoon transforms its treasure hoard into readable scrolls!
"""

import tempfile
import sys
from pathlib import Path
from typing import Union
from racgoat.models.comments import (
    ReviewSession,
    FileReview,
    SerializableComment,
    LineComment,
    RangeComment,
    FileComment,
)


def serialize_review_session(session: ReviewSession) -> str:
    """Serialize ReviewSession to Markdown format.

    Args:
        session: ReviewSession containing comments and metadata

    Returns:
        Markdown string with proper heading structure

    Format:
        # Code Review

        **Branch**: {branch_name}
        **Commit**: {commit_sha}

        ## File: {file_path}

        ### Line {N} / Lines {N}-{M} / File-level comment
        {comment_text}

    Notes:
        - Files sorted alphabetically
        - Comments within file ordered by addition (preserved order)
        - Comment text preserved exactly (no Markdown escaping)
    """
    lines = []

    # Header section
    lines.append("# Code Review")
    lines.append("")
    lines.append(f"**Branch**: {session.branch_name}")
    lines.append(f"**Commit**: {session.commit_sha}")
    lines.append("")

    # File sections (alphabetically sorted)
    for file_path in sorted(session.file_reviews.keys()):
        review = session.file_reviews[file_path]
        lines.append(f"## File: {file_path}")
        lines.append("")

        # Comments within file (preserve order)
        for comment in review.comments:
            # Generate heading based on comment type
            if isinstance(comment, LineComment):
                lines.append(f"### Line {comment.line_number}")
            elif isinstance(comment, RangeComment):
                lines.append(f"### Lines {comment.start_line}-{comment.end_line}")
            elif isinstance(comment, FileComment):
                lines.append("### File-level comment")
            else:
                # Fallback for unknown comment types
                lines.append("### Comment")

            # Comment text (preserve Markdown chars, no escaping)
            lines.append(comment.text)
            lines.append("")

    # Join with newlines
    return "\n".join(lines)


def write_markdown_output(content: str, output_path: Union[str, Path]) -> None:
    """Write Markdown content to file with atomic operation.

    Args:
        content: Markdown string to write
        output_path: Destination file path

    Raises:
        FileExistsError: If output_path already exists
        OSError: On write failures (permissions, invalid path, disk full)

    Notes:
        - Atomic write: temp file + rename (prevents partial files)
        - UTF-8 encoding
        - Never overwrites existing files (raises FileExistsError)
        - Logs errors to stderr
    """
    output_path = Path(output_path)

    # Check if file already exists
    if output_path.exists():
        # Log FileExistsError
        print(f"[ERROR] FileExistsError: Output file already exists: {output_path}", file=sys.stderr)
        raise FileExistsError(f"Output file already exists: {output_path}")

    # Atomic write: temp file + rename
    temp_path = None
    try:
        # Create temp file in same directory (ensures same filesystem for atomic rename)
        temp_fd, temp_name = tempfile.mkstemp(
            dir=output_path.parent,
            prefix=".racgoat_",
            suffix=".md.tmp"
        )
        temp_path = Path(temp_name)

        # Write content to temp file
        with open(temp_fd, 'w', encoding='utf-8') as f:
            f.write(content)

        # Atomic rename (overwrites if needed, but we already checked above)
        temp_path.rename(output_path)

    except OSError as e:
        # Log OSError details (permissions, invalid path, disk full, etc.)
        print(f"[ERROR] OSError writing to {output_path}: {e} (errno: {e.errno})", file=sys.stderr)
        # Clean up temp file on error
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise

    except Exception as e:
        # Log unexpected errors
        print(f"[ERROR] Unexpected error writing to {output_path}: {type(e).__name__}: {e}", file=sys.stderr)
        # Clean up temp file on error
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise
