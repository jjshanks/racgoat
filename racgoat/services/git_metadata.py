"""Git metadata extraction service (Milestone 4).

Extracts branch name and commit SHA from the current git repository.
Provides graceful fallback when git is unavailable or commands fail.

The raccoon sniffs out the git tree's secrets!
"""

import subprocess
from typing import Tuple


def get_git_metadata() -> Tuple[str, str]:
    """Extract current git branch name and commit SHA.

    Returns:
        Tuple of (branch_name, commit_sha)
        - branch_name: Current branch (or "Unknown Branch" if unavailable)
        - commit_sha: Full commit SHA (or "Unknown SHA" if unavailable)

    Notes:
        - Never raises exceptions (always returns placeholders on error)
        - Timeout after 2 seconds (prevents hanging on slow git operations)
        - Uses `git` CLI (no external dependencies)

    Examples:
        >>> branch, sha = get_git_metadata()
        >>> assert branch != "Unknown Branch"  # In actual repo
        >>> assert len(sha) == 40  # Full SHA
    """
    try:
        # Extract branch name
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2
        )
        branch_name = branch_result.stdout.strip()

        # Extract commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2
        )
        commit_sha = sha_result.stdout.strip()

        return (branch_name, commit_sha)

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        # Any git error → return placeholders
        return ("Unknown Branch", "Unknown SHA")
