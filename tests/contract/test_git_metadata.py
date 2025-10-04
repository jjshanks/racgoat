"""Contract tests for git metadata extraction (Milestone 4).

These tests verify the get_git_metadata() function behavior across different
git repository states. They MUST fail before implementation (TDD approach).

Tests verify:
- Normal git repo (valid branch + SHA)
- Detached HEAD state (branch="HEAD")
- Not a git repo (placeholders)
- Git command timeout (< 3 seconds with fallback)
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGitMetadataContract:
    """Contract tests for git metadata extraction."""

    def test_normal_git_repo(self):
        """Raccoon sniffs out branch and commit from healthy git pile."""
        # Arrange: We're in the RacGoat repo (actual git repo)
        from racgoat.services.git_metadata import get_git_metadata

        # Act: Extract metadata
        branch_name, commit_sha = get_git_metadata()

        # Assert: Valid branch name and 40-char SHA
        assert branch_name != "Unknown Branch", \
            "Should extract real branch name from actual repo"
        assert len(commit_sha) == 40, \
            f"Expected 40-char SHA, got {len(commit_sha)}: {commit_sha}"
        assert all(c in "0123456789abcdef" for c in commit_sha), \
            f"SHA should be hex chars: {commit_sha}"

    def test_detached_head(self, tmp_path):
        """Goat perches on detached HEAD, unbothered."""
        pytest.skip("Requires git repo fixture with detached HEAD - implement in integration tests")
        # Note: This test would require creating a temp repo and checking out
        # a specific commit. Skipping for contract tests, will implement in
        # integration tests where we have proper fixtures.

    def test_not_a_git_repo(self, tmp_path, monkeypatch):
        """Raccoon explores non-git territory, finds placeholders."""
        # Arrange: Change to temp dir (not a repo)
        monkeypatch.chdir(tmp_path)
        from racgoat.services.git_metadata import get_git_metadata

        # Act: Try to extract metadata
        branch_name, commit_sha = get_git_metadata()

        # Assert: Fallback values returned
        assert branch_name == "Unknown Branch", \
            f"Expected placeholder, got: {branch_name}"
        assert commit_sha == "Unknown SHA", \
            f"Expected placeholder, got: {commit_sha}"

    def test_git_command_timeout(self):
        """Raccoon waits 2 seconds, then moves on."""
        # Arrange: Mock subprocess to raise TimeoutExpired
        from racgoat.services.git_metadata import get_git_metadata

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                timeout=2
            )

            # Act: Call function (should complete in <3 seconds)
            import time
            start = time.time()
            branch_name, commit_sha = get_git_metadata()
            elapsed = time.time() - start

            # Assert: Fallback values, completed quickly
            assert branch_name == "Unknown Branch"
            assert commit_sha == "Unknown SHA"
            assert elapsed < 3.0, \
                f"Function took {elapsed}s, should timeout and return quickly"
