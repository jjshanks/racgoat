"""Dependency Injection Container for RacGoat Services.

A central service registry that manages all application services with lazy
initialization and clean dependency management.

The raccoon's treasure map - all services organized in one central cache!
"""

from typing import Optional

from racgoat.services.comment_store import CommentStore
from racgoat.services.git_metadata import get_git_metadata
from racgoat.services.markdown_writer import (
    serialize_review_session,
    write_markdown_output,
)


class ServiceContainer:
    """Central container for all application services.

    Manages service instances with lazy initialization. Services are created
    only when first accessed, reducing startup overhead.

    Pattern:
        - Singleton instances for stateful services (CommentStore)
        - Function references for stateless utilities (git_metadata, markdown_writer)
        - Clean separation: App creates container, controllers access services

    Usage:
        >>> container = ServiceContainer()
        >>> comment_store = container.comment_store
        >>> branch, sha = container.get_git_metadata()

    The goat climbs the dependency tree with sure-footed precision!
    """

    def __init__(self):
        """Initialize the service container with lazy-loaded services."""
        # Stateful services (lazy-initialized)
        self._comment_store: Optional[CommentStore] = None

        # Stateless service functions (no initialization needed)
        self.get_git_metadata = get_git_metadata
        self.serialize_review_session = serialize_review_session
        self.write_markdown_output = write_markdown_output

    @property
    def comment_store(self) -> CommentStore:
        """Get or create the comment store instance.

        Returns:
            CommentStore: Singleton comment store instance

        The raccoon's treasure cache - created once, used everywhere!
        """
        if self._comment_store is None:
            self._comment_store = CommentStore()
        return self._comment_store

    def reset(self) -> None:
        """Reset all service instances (for testing).

        Clears the comment store and recreates service instances.
        Useful for test isolation and cleanup.

        The raccoon dumps its treasure and starts fresh!
        """
        self._comment_store = None
