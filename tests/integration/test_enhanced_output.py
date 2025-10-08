"""Integration tests for enhanced markdown output format.

These tests validate end-to-end functionality of the enhanced markdown format
with all comment types, code context, and edge cases.
"""

import pytest
import tempfile
import os
from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType
from datetime import datetime


class TestEnhancedOutputIntegration:
    """Integration tests for complete enhanced markdown output."""

    @pytest.mark.asyncio
    async def test_end_to_end_with_all_comment_types(self):
        """Complete workflow with line, range, and file comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            # Create diff with multiple files and hunks
            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="auth.py",
                    added_lines=5,
                    removed_lines=2,
                    hunks=[
                        DiffHunk(
                            old_start=1,
                            new_start=1,
                            lines=[
                                (' ', 'import hashlib'),
                                ('-', 'def login(user):'),
                                ('+', 'def login(user, password):'),
                                ('+', '    # Validate input'),
                                ('+', '    if not user or not password:'),
                                ('+', '        raise ValueError("Missing credentials")'),
                                (' ', '    db.query(user)'),
                                (' ', '    return user'),
                            ]
                        )
                    ]
                ),
                DiffFile(
                    file_path="utils.py",
                    added_lines=3,
                    hunks=[
                        DiffHunk(
                            old_start=1,
                            new_start=1,
                            lines=[
                                ('+', 'def sanitize(input):'),
                                ('+', '    return input.strip()'),
                                ('+', '    # TODO: Add more validation'),
                            ]
                        )
                    ]
                )
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add different comment types
                # Line comment
                app.comment_store.add(Comment(
                    text="Add input validation before database query",
                    target=CommentTarget(file_path="auth.py", line_number=2),
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                ))

                # Range comment
                app.comment_store.add(Comment(
                    text="This validation block looks good",
                    target=CommentTarget(file_path="auth.py", line_range=(3, 5)),
                    timestamp=datetime.now(),
                    comment_type=CommentType.RANGE
                ))

                # File comment
                app.comment_store.add(Comment(
                    text="Consider adding unit tests for this module",
                    target=CommentTarget(file_path="utils.py"),
                    timestamp=datetime.now(),
                    comment_type=CommentType.FILE
                ))

                # Trigger save by calling action_quit directly
                app.action_quit()

            # Verify output file
            assert os.path.exists(output_file), "Output file not created"

            with open(output_file, 'r') as f:
                content = f.read()

            # Verify YAML frontmatter
            assert content.startswith("---\n"), "YAML frontmatter missing"
            assert 'review_id:' in content
            assert 'files_reviewed: 2' in content
            assert 'total_comments: 3' in content

            # Verify HTML metadata for all comments
            assert 'id: c1' in content
            assert 'id: c2' in content
            assert 'id: c3' in content
            assert 'status: open' in content

            # Verify line/range fields
            assert 'line: 2' in content  # Line comment
            assert 'lines: 3-5' in content  # Range comment
            # File comment should not have line/lines field

            # Verify code context
            assert '**Context**:' in content
            assert '```' in content
            assert '2 | def login(user, password):' in content

            # Verify comment text
            assert "Add input validation before database query" in content
            assert "This validation block looks good" in content
            assert "Consider adding unit tests for this module" in content

    @pytest.mark.asyncio
    async def test_edge_case_malformed_hunk(self):
        """Code context should be skipped for malformed hunks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            # Create diff with malformed hunk
            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="broken.py",
                    added_lines=0,
                    removed_lines=0,
                    hunks=[
                        DiffHunk(
                            old_start=1,
                            new_start=1,
                            lines=[],
                            is_malformed=True,
                            raw_text="@@ -1,5 +1,5 @@ invalid",
                            parse_error="Invalid header format"
                        )
                    ]
                )
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comment on line within malformed hunk
                app.comment_store.add(Comment(
                    text="This might be broken",
                    target=CommentTarget(file_path="broken.py", line_number=3),
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                ))

                app.action_quit()

            # Verify output
            with open(output_file, 'r') as f:
                content = f.read()

            # Comment should be present
            assert "This might be broken" in content
            # But context should be skipped (malformed hunk)
            assert "**Context**:" not in content or content.count("**Context**:") == 0

    @pytest.mark.asyncio
    async def test_edge_case_context_at_file_boundaries(self):
        """Code context should handle file start/end gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            # Create diff with small file
            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="small.py",
                    added_lines=2,
                    hunks=[
                        DiffHunk(
                            old_start=1,
                            new_start=1,
                            lines=[
                                ('+', 'line1'),
                                ('+', 'line2'),
                            ]
                        )
                    ]
                )
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Comment on first line (no context before)
                app.comment_store.add(Comment(
                    text="First line comment",
                    target=CommentTarget(file_path="small.py", line_number=1),
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                ))

                app.action_quit()

            # Verify output
            with open(output_file, 'r') as f:
                content = f.read()

            # Should still have context (just limited)
            assert "1 | line1" in content
            # Should include following line as context
            assert "2 | line2" in content

    @pytest.mark.asyncio
    async def test_multiple_files_sequential_ids(self):
        """Comment IDs should be sequential across files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="a.py",
                    added_lines=1,
                    hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'a')])]
                ),
                DiffFile(
                    file_path="b.py",
                    added_lines=1,
                    hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'b')])]
                ),
                DiffFile(
                    file_path="c.py",
                    added_lines=1,
                    hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'c')])]
                )
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comments across files
                for file_path in ['a.py', 'b.py', 'c.py']:
                    app.comment_store.add(Comment(
                        text=f"Comment on {file_path}",
                        target=CommentTarget(file_path=file_path, line_number=1),
                        timestamp=datetime.now(),
                        comment_type=CommentType.LINE
                    ))

                app.action_quit()

            # Verify sequential IDs
            with open(output_file, 'r') as f:
                content = f.read()

            assert 'id: c1' in content
            assert 'id: c2' in content
            assert 'id: c3' in content

    @pytest.mark.asyncio
    async def test_horizontal_rules_across_files(self):
        """Horizontal rules should separate comments within files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="test.py",
                    added_lines=3,
                    hunks=[
                        DiffHunk(
                            old_start=1,
                            new_start=1,
                            lines=[
                                ('+', 'line1'),
                                ('+', 'line2'),
                                ('+', 'line3')
                            ]
                        )
                    ]
                )
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add 3 comments
                for i in range(1, 4):
                    app.comment_store.add(Comment(
                        text=f"Comment {i}",
                        target=CommentTarget(file_path="test.py", line_number=i),
                        timestamp=datetime.now(),
                        comment_type=CommentType.LINE
                    ))

                app.action_quit()

            # Verify horizontal rules
            with open(output_file, 'r') as f:
                content = f.read()

            # Count standalone --- (excluding YAML frontmatter)
            lines = content.split('\n')
            hr_count = sum(1 for line in lines if line.strip() == '---')
            # Should have 2 YAML delimiters + 2 HRs between 3 comments
            assert hr_count >= 4, f"Expected at least 4 '---', got {hr_count}"
