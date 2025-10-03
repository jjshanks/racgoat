"""Contract tests for CommentStore API.

These tests validate the CommentStore service contract BEFORE implementation.
All tests should FAIL initially (TDD red phase).
"""

import pytest
from datetime import datetime


def test_raccoon_stashes_single_line_comment():
    """A raccoon can stash a single shiny comment on one line."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()
    target = CommentTarget(
        file_path="trash/bin.py",
        line_number=42,
        line_range=None
    )
    comment = Comment(
        text="This trash needs recycling",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )

    store.add(comment)

    # Retrieve the stashed treasure
    retrieved = store.get("trash/bin.py", 42)
    assert len(retrieved) == 1
    assert retrieved[0].text == "This trash needs recycling"
    assert retrieved[0].target.line_number == 42


def test_goat_bleats_file_level_wisdom():
    """A goat can bleat wisdom about an entire file from the mountain top."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()
    target = CommentTarget(
        file_path="mountain/cliff.py",
        line_number=None,
        line_range=None
    )
    comment = Comment(
        text="This whole cliff is too steep",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.FILE
    )

    store.add(comment)

    # Goat wisdom echoes back
    retrieved = store.get("mountain/cliff.py", None)
    assert len(retrieved) == 1
    assert retrieved[0].text == "This whole cliff is too steep"
    assert retrieved[0].target.line_number is None
    assert retrieved[0].target.line_range is None


def test_raccoon_marks_trash_range():
    """A raccoon can mark an entire range of trash cans as treasure."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()
    target = CommentTarget(
        file_path="alley/dumpster.py",
        line_number=None,
        line_range=(10, 15)
    )
    comment = Comment(
        text="Best trash collection ever",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.RANGE
    )

    store.add(comment)

    # Every line in the range has the same treasure marker
    for line in range(10, 16):
        retrieved = store.get("alley/dumpster.py", line)
        assert len(retrieved) == 1
        assert retrieved[0].text == "Best trash collection ever"


def test_empty_cache_returns_no_treasures():
    """Looking for treasure in an empty cache returns nothing (sad raccoon noises)."""
    from racgoat.services.comment_store import CommentStore

    store = CommentStore()
    retrieved = store.get("nonexistent/file.py", 999)

    assert retrieved == []
    assert len(retrieved) == 0


def test_goat_and_raccoon_both_claim_same_line():
    """Both goat and raccoon can leave marks on the same line (overlap!)."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # Raccoon's line comment
    target1 = CommentTarget(file_path="shared/rock.py", line_number=20, line_range=None)
    comment1 = Comment(
        text="Raccoon was here",
        target=target1,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )
    store.add(comment1)

    # Goat's range comment overlapping the same line
    target2 = CommentTarget(file_path="shared/rock.py", line_number=None, line_range=(15, 25))
    comment2 = Comment(
        text="Goat climbed here",
        target=target2,
        timestamp=datetime.now(),
        comment_type=CommentType.RANGE
    )
    store.add(comment2)

    # Both marks visible on line 20
    retrieved = store.get("shared/rock.py", 20)
    assert len(retrieved) == 2
    assert any(c.text == "Raccoon was here" for c in retrieved)
    assert any(c.text == "Goat climbed here" for c in retrieved)


def test_trash_hoard_capacity_limit():
    """Raccoons can't hoard more than 100 treasures (constitutional limit!)."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # Add 100 comments (at capacity)
    for i in range(100):
        target = CommentTarget(file_path=f"file_{i}.py", line_number=1, line_range=None)
        comment = Comment(
            text=f"Comment {i}",
            target=target,
            timestamp=datetime.now(),
            comment_type=CommentType.LINE
        )
        store.add(comment)

    assert store.count() == 100

    # 101st comment should raise error
    target = CommentTarget(file_path="overflow.py", line_number=1, line_range=None)
    comment = Comment(
        text="One too many",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )

    with pytest.raises(ValueError, match="limit"):
        store.add(comment)


def test_raccoon_updates_cached_thought():
    """A raccoon can update a previously cached thought (edit existing comment)."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # Original thought
    target = CommentTarget(file_path="cache/thought.py", line_number=10, line_range=None)
    original = Comment(
        text="Original treasure",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )
    store.add(original)

    # Update the thought
    store.update(target, "Updated treasure")

    # Verify update
    retrieved = store.get("cache/thought.py", 10)
    assert len(retrieved) == 1
    assert retrieved[0].text == "Updated treasure"
    # Timestamp should be unchanged (original creation time preserved)


def test_goat_kicks_away_unwanted_mark():
    """A goat can kick away an unwanted mark (delete comment)."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # Add a mark
    target = CommentTarget(file_path="cliff/edge.py", line_number=5, line_range=None)
    comment = Comment(
        text="Bad footing here",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )
    store.add(comment)

    # Goat kicks it away
    store.delete(target)

    # Mark is gone
    retrieved = store.get("cliff/edge.py", 5)
    assert retrieved == []


def test_cleanup_crew_clears_all_caches():
    """The cleanup crew can clear all cached treasures at once."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # Add multiple comments
    for i in range(10):
        target = CommentTarget(file_path=f"cleanup_{i}.py", line_number=1, line_range=None)
        comment = Comment(
            text=f"Comment {i}",
            target=target,
            timestamp=datetime.now(),
            comment_type=CommentType.LINE
        )
        store.add(comment)

    assert store.count() == 10

    # Clear all
    store.clear()

    assert store.count() == 0
    # All caches empty
    for i in range(10):
        assert store.get(f"cleanup_{i}.py", 1) == []


def test_empty_comment_text_angers_raccoon():
    """Empty treasure text makes the raccoon angry (ValueError raised)."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()
    target = CommentTarget(file_path="empty/void.py", line_number=1, line_range=None)

    # Empty text
    comment = Comment(
        text="",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )

    with pytest.raises(ValueError, match="empty"):
        store.add(comment)

    # Whitespace-only text also invalid
    comment.text = "   "
    with pytest.raises(ValueError, match="empty"):
        store.add(comment)


def test_raccoon_knows_if_cache_exists():
    """A raccoon can quickly check if treasure exists without fetching it."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # No treasure yet
    assert store.has_comment("test.py", 42) is False

    # Add treasure
    target = CommentTarget(file_path="test.py", line_number=42, line_range=None)
    comment = Comment(
        text="Treasure found",
        target=target,
        timestamp=datetime.now(),
        comment_type=CommentType.LINE
    )
    store.add(comment)

    # Now it exists
    assert store.has_comment("test.py", 42) is True


def test_get_all_file_treasures():
    """Get all treasures (comments) for a file, regardless of type."""
    from racgoat.services.comment_store import CommentStore
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    store = CommentStore()

    # File-level comment
    target1 = CommentTarget(file_path="multi.py", line_number=None, line_range=None)
    comment1 = Comment(text="File comment", target=target1, timestamp=datetime.now(), comment_type=CommentType.FILE)
    store.add(comment1)

    # Line comment
    target2 = CommentTarget(file_path="multi.py", line_number=10, line_range=None)
    comment2 = Comment(text="Line comment", target=target2, timestamp=datetime.now(), comment_type=CommentType.LINE)
    store.add(comment2)

    # Range comment
    target3 = CommentTarget(file_path="multi.py", line_number=None, line_range=(20, 25))
    comment3 = Comment(text="Range comment", target=target3, timestamp=datetime.now(), comment_type=CommentType.RANGE)
    store.add(comment3)

    # Get all for file
    all_comments = store.get_file_comments("multi.py")

    # Should have file-level (1) + line (1) + range entries (6 lines) = unique comments only
    # Contract specifies unique comments, not per-line entries
    assert len(all_comments) >= 3  # At minimum: file, line, range

    # Verify types present
    types = {c.comment_type for c in all_comments}
    assert CommentType.FILE in types
    assert CommentType.LINE in types
    assert CommentType.RANGE in types
