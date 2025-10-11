"""Performance tests for diff segment extraction (Feature 007).

Validates that diff segment extraction meets performance requirements.

The raccoon's treasure transformation spell must be fast!
"""

import time
import pytest
from racgoat.services.markdown_writer import extract_diff_segment
from racgoat.parser.models import DiffFile, DiffHunk


class TestDiffSegmentPerformance:
    """Performance tests for extract_diff_segment() function."""

    def test_diff_segment_extraction_performance(self):
        """Validate <100ms for 100 comments (SC-004)."""
        # Setup: Create large hunk with 1000 lines
        large_lines = [(' ', f'line {i}') for i in range(1000)]
        large_hunk = DiffHunk(old_start=1, new_start=1, lines=large_lines)
        diff_file = DiffFile(file_path="large.py", hunks=[large_hunk])

        # Execute: Extract diff segments for 100 comments
        start = time.perf_counter()
        for i in range(100):
            # Extract segment at every 10th line
            extract_diff_segment(diff_file, line_number=(i * 10) + 1)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 100, f"Extraction took {elapsed_ms:.2f}ms (expected <100ms)"

    def test_large_hunk_extraction_performance(self):
        """Validate performance with very large hunks (10k lines)."""
        # Setup: Create very large hunk
        very_large_lines = [(' ', f'line {i}') for i in range(10000)]
        very_large_hunk = DiffHunk(old_start=1, new_start=1, lines=very_large_lines)
        diff_file = DiffFile(file_path="huge.py", hunks=[very_large_hunk])

        # Execute: Single extraction should be fast
        start = time.perf_counter()
        result = extract_diff_segment(diff_file, line_number=5000)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 50, f"Single extraction took {elapsed_ms:.2f}ms (expected <50ms)"
        assert result is not None

    def test_multiple_hunks_performance(self):
        """Validate performance with multiple hunks."""
        # Setup: Create 50 small hunks
        hunks = []
        for i in range(50):
            hunk = DiffHunk(
                old_start=i * 100,
                new_start=i * 100,
                lines=[(' ', f'hunk {i} line {j}') for j in range(50)]
            )
            hunks.append(hunk)

        diff_file = DiffFile(file_path="multi_hunk.py", hunks=hunks)

        # Execute: Extract from different hunks
        start = time.perf_counter()
        for i in range(50):
            # Extract one line from each hunk
            extract_diff_segment(diff_file, line_number=(i * 100) + 25)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 100, f"Multi-hunk extraction took {elapsed_ms:.2f}ms (expected <100ms)"
