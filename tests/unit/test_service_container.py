"""Tests for ServiceContainer (Dependency Injection).

The raccoon tests its treasure map organization!
"""

from racgoat.di import ServiceContainer
from racgoat.services.comment_store import CommentStore


def test_service_container_creates_comment_store():
    """Test that ServiceContainer creates a CommentStore instance."""
    container = ServiceContainer()
    comment_store = container.comment_store

    assert isinstance(comment_store, CommentStore)


def test_service_container_returns_same_comment_store():
    """Test that ServiceContainer returns the same CommentStore instance (singleton)."""
    container = ServiceContainer()
    comment_store1 = container.comment_store
    comment_store2 = container.comment_store

    assert comment_store1 is comment_store2


def test_service_container_provides_git_metadata():
    """Test that ServiceContainer provides git metadata function."""
    container = ServiceContainer()

    assert callable(container.get_git_metadata)

    # Test that it returns a tuple
    branch, sha = container.get_git_metadata()
    assert isinstance(branch, str)
    assert isinstance(sha, str)


def test_service_container_provides_markdown_writer():
    """Test that ServiceContainer provides markdown writer functions."""
    container = ServiceContainer()

    assert callable(container.serialize_review_session)
    assert callable(container.write_markdown_output)


def test_service_container_reset():
    """Test that ServiceContainer.reset() clears services."""
    container = ServiceContainer()

    # Create comment store and add a comment
    comment_store1 = container.comment_store
    from racgoat.models.comments import Comment, CommentTarget, CommentType

    comment = Comment(
        text="Test comment",
        target=CommentTarget(file_path="test.py", line_number=1),
        comment_type=CommentType.LINE,
    )
    comment_store1.add(comment)
    assert comment_store1.count() == 1

    # Reset the container
    container.reset()

    # Get new comment store - should be empty
    comment_store2 = container.comment_store
    assert comment_store2.count() == 0

    # Should be a new instance
    assert comment_store1 is not comment_store2
