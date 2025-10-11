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
from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary
from racgoat.constants import DEFAULT_CONTEXT_LINES


def extract_diff_segment(
    diff_file: DiffFile,
    line_number: int | None = None,
    line_range: tuple[int, int] | None = None,
    context_lines: int = DEFAULT_CONTEXT_LINES
) -> str | None:
    """Extract diff segment from hunks for a comment.

    Args:
        diff_file: DiffFile containing hunks to search
        line_number: Target line number for line comments (post-change)
        line_range: Target line range for range comments (start, end) (post-change)
        context_lines: Number of context lines before/after target (default: DEFAULT_CONTEXT_LINES)

    Returns:
        Formatted diff segment with +/- markers, or None if unavailable

    Logic:
        - For line comments: Extract ±context_lines around line_number
        - For range comments: Extract ±context_lines around range boundaries
        - For file comments (both None): Return None
        - Include removed lines ('-') in the context window
        - Format: "{marker}{content}" (no space after marker)
        - Markers: '+' for added, '-' for removed, ' ' for context
    """
    # File-level comment - no segment
    if line_number is None and line_range is None:
        return None

    # Determine target range
    if line_number is not None:
        target_start = line_number
        target_end = line_number
    else:
        if line_range is None:
            return None
        target_start, target_end = line_range

    # Find hunk containing target line(s)
    relevant_hunk = None
    for hunk in diff_file.hunks:
        # Skip malformed hunks
        if hunk.is_malformed:
            continue

        # Calculate line range for this hunk (post-change)
        hunk_start = hunk.new_start
        # Count added and context lines to find end
        new_line_count = sum(1 for change_type, _ in hunk.lines if change_type in ('+', ' '))
        hunk_end = hunk_start + new_line_count - 1

        # Check if target is within this hunk
        if hunk_start <= target_start <= hunk_end:
            relevant_hunk = hunk
            break

    # No hunk found
    if relevant_hunk is None:
        return None

    # Build diff segment with line markers
    diff_lines = []
    current_new_line = relevant_hunk.new_start

    # Calculate context window
    context_start = max(target_start - context_lines, relevant_hunk.new_start)
    context_end = target_end + context_lines

    for change_type, content in relevant_hunk.lines:
        in_window = False

        # Determine if line is within context window
        if change_type == '-':
            # Removed line: associate with current new_line position
            in_window = (context_start <= current_new_line <= context_end)
        elif change_type in ('+', ' '):
            # Added or context line: check against new_line position
            in_window = (context_start <= current_new_line <= context_end)
            current_new_line += 1

        # Include line if in window
        if in_window:
            diff_lines.append(f"{change_type}{content}")

    # Format as diff segment
    if not diff_lines:
        return None

    return "\n".join(diff_lines)


def format_file_stats(diff_file: DiffFile) -> str:
    """Format statistical summary for file-level comments.

    Args:
        diff_file: DiffFile containing hunks and line counts

    Returns:
        String like "5 hunks, +120 -45 lines"
    """
    hunk_count = len(diff_file.hunks)
    return f"{hunk_count} hunks, +{diff_file.added_lines} -{diff_file.removed_lines} lines"


def serialize_review_session(session: ReviewSession, diff_summary: DiffSummary | None = None) -> str:
    """Serialize ReviewSession to Markdown format with enhanced metadata.

    Args:
        session: ReviewSession containing comments and metadata
        diff_summary: Optional DiffSummary for code context extraction

    Returns:
        Markdown string with YAML frontmatter, HTML metadata, and code context

    Format:
        ---
        review_id: "{review_id}"
        branch: "{branch_name}"
        base_commit: "{commit_sha}"
        files_reviewed: {count}
        total_comments: {count}
        ---

        # Code Review

        ## File: `{file_path}`

        <!--comment
        id: c{N}
        status: open
        line: {N}
        -->
        ### Line {N} / Lines {N}-{M} / File-level comment
        {comment_text}

        **Context**:
        ```
        {line_num} | {code}
        ```
        ---

    Notes:
        - YAML frontmatter contains review metadata
        - HTML comments contain per-comment metadata
        - Code context included if diff_summary provided
        - Files sorted alphabetically
        - Comments within file ordered by addition (preserved order)
        - Comment text preserved exactly (no Markdown escaping)
        - Horizontal rules separate comments
    """
    lines = []

    # YAML Frontmatter
    lines.append("---")
    lines.append(f'review_id: "{session.review_id}"')
    lines.append(f'branch: "{session.branch_name}"')
    lines.append(f'base_commit: "{session.commit_sha}"')
    lines.append(f'files_reviewed: {session.files_reviewed}')
    lines.append(f'total_comments: {session.total_comment_count}')
    lines.append("---")
    lines.append("")

    # Header section
    lines.append("# Code Review")
    lines.append("")

    # Build file_path → DiffFile map for context extraction
    file_map = {}
    if diff_summary:
        for diff_file in diff_summary.files:
            file_map[diff_file.file_path] = diff_file

    # Sequential comment ID counter
    comment_counter = 1

    # File sections (alphabetically sorted)
    for file_path in sorted(session.file_reviews.keys()):
        review = session.file_reviews[file_path]
        lines.append(f"## File: `{file_path}`")
        lines.append("")

        # Get DiffFile for context extraction
        diff_file = file_map.get(file_path)

        # Comments within file (preserve order)
        for idx, comment in enumerate(review.comments):
            # HTML metadata block
            lines.append("<!--comment")
            lines.append(f"id: c{comment_counter}")
            lines.append(f"status: {comment.status}")

            # Add line/lines field based on comment type
            if isinstance(comment, LineComment):
                lines.append(f"line: {comment.line_number}")
            elif isinstance(comment, RangeComment):
                lines.append(f"lines: {comment.start_line}-{comment.end_line}")
            # FileComment: no line field

            lines.append("-->")

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

            # Code context (if available)
            if diff_file:
                if isinstance(comment, LineComment):
                    diff_segment = extract_diff_segment(diff_file, line_number=comment.line_number)
                    if diff_segment:
                        lines.append("**Context**:")
                        lines.append("```diff")
                        lines.append(diff_segment)
                        lines.append("```")
                        lines.append("")
                elif isinstance(comment, RangeComment):
                    diff_segment = extract_diff_segment(
                        diff_file,
                        line_range=(comment.start_line, comment.end_line)
                    )
                    if diff_segment:
                        lines.append("**Context**:")
                        lines.append("```diff")
                        lines.append(diff_segment)
                        lines.append("```")
                        lines.append("")
                elif isinstance(comment, FileComment):
                    # File-level comment shows statistical summary
                    stats = format_file_stats(diff_file)
                    lines.append(f"**File changes**: {stats}")
                    lines.append("")

            # Horizontal rule separator (not after last comment in file)
            if idx < len(review.comments) - 1:
                lines.append("---")
                lines.append("")

            # Increment comment counter
            comment_counter += 1

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
