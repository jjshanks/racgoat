"""Pytest configuration and shared fixtures for RacGoat tests.

The raccoon's test toolkit - reusable across all tests!
"""

import os


def get_perf_threshold(local_ms: int) -> int:
    """Get performance threshold adjusted for CI environment.

    Local development gets strict thresholds to catch regressions early.
    CI environments get relaxed thresholds (2x) to handle shared runner overhead.

    Args:
        local_ms: Strict threshold for local development (in milliseconds)

    Returns:
        Threshold in milliseconds (2x for CI, original for local)

    Example:
        >>> # In local dev: CI env var not set
        >>> get_perf_threshold(1000)
        1000
        >>> # In GitHub Actions: CI=true
        >>> os.environ['CI'] = 'true'
        >>> get_perf_threshold(1000)
        2000
    """
    if os.getenv('CI'):
        return local_ms * 2  # Relax thresholds in CI
    return local_ms
