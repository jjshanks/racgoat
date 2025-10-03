#!/usr/bin/env python3
"""Generate large diff files for performance testing.

This raccoon builds big treasure piles to test the goat's climbing speed!

Usage:
    python scripts/generate_large_diff.py --files 100 --lines-per-file 100 > large.diff
    python scripts/generate_large_diff.py --preset max > max.diff
"""

import argparse
import sys
from typing import TextIO


def generate_file_diff(
    file_index: int,
    lines_added: int,
    lines_removed: int,
    lines_context: int = 3,
) -> str:
    """Generate a single file's diff section.

    Args:
        file_index: File number (for unique naming)
        lines_added: Number of added lines to generate
        lines_removed: Number of removed lines to generate
        lines_context: Number of context lines per hunk

    Returns:
        Diff text for one file
    """
    file_name = f"src/module_{file_index:04d}/component_{file_index:04d}.py"

    # Diff header
    diff = f"diff --git a/{file_name} b/{file_name}\n"
    diff += f"index {'a'*7}..{'b'*7} 100644\n"
    diff += f"--- a/{file_name}\n"
    diff += f"+++ b/{file_name}\n"

    # Generate hunks (group changes into chunks)
    old_line = 1
    new_line = 1
    total_generated_added = 0
    total_generated_removed = 0

    # Create multiple hunks to simulate realistic diff
    while total_generated_added < lines_added or total_generated_removed < lines_removed:
        # Calculate hunk size (distribute remaining lines)
        hunk_added = min(10, lines_added - total_generated_added)
        hunk_removed = min(10, lines_removed - total_generated_removed)

        if hunk_added == 0 and hunk_removed == 0:
            break

        # Hunk header
        old_count = hunk_removed + lines_context * 2
        new_count = hunk_added + lines_context * 2
        diff += f"@@ -{old_line},{old_count} +{new_line},{new_count} @@\n"

        # Leading context
        for i in range(lines_context):
            diff += f" def context_line_{old_line + i}():\n"

        # Removed lines
        for i in range(hunk_removed):
            diff += f"-    # Old implementation line {total_generated_removed + i + 1}\n"

        # Added lines
        for i in range(hunk_added):
            diff += f"+    # New implementation line {total_generated_added + i + 1}\n"

        # Trailing context
        for i in range(lines_context):
            diff += f" def context_line_{old_line + old_count - lines_context + i}():\n"

        # Update counters
        total_generated_added += hunk_added
        total_generated_removed += hunk_removed
        old_line += old_count
        new_line += new_count

    return diff


def generate_large_diff(
    num_files: int,
    lines_per_file: int,
    output: TextIO = sys.stdout,
) -> None:
    """Generate a large diff with specified parameters.

    Args:
        num_files: Number of files to include in diff
        lines_per_file: Average lines changed per file
        output: Output stream (default: stdout)
    """
    for file_idx in range(num_files):
        # Vary the distribution: some files with more adds, some with more removes
        if file_idx % 3 == 0:
            # More additions
            added = int(lines_per_file * 0.7)
            removed = int(lines_per_file * 0.3)
        elif file_idx % 3 == 1:
            # More removals
            added = int(lines_per_file * 0.3)
            removed = int(lines_per_file * 0.7)
        else:
            # Balanced
            added = int(lines_per_file * 0.5)
            removed = int(lines_per_file * 0.5)

        diff_text = generate_file_diff(file_idx, added, removed)
        output.write(diff_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate large diff files for performance testing"
    )
    parser.add_argument(
        "--files",
        type=int,
        default=100,
        help="Number of files in diff (default: 100)",
    )
    parser.add_argument(
        "--lines-per-file",
        type=int,
        default=100,
        help="Average lines changed per file (default: 100)",
    )
    parser.add_argument(
        "--preset",
        choices=["small", "medium", "large", "max"],
        help="Use preset configuration (overrides --files and --lines-per-file)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    # Apply preset if specified
    if args.preset == "small":
        num_files = 10
        lines_per_file = 50
    elif args.preset == "medium":
        num_files = 50
        lines_per_file = 100
    elif args.preset == "large":
        num_files = 100
        lines_per_file = 100
    elif args.preset == "max":
        # PRD requirement: up to 100 files, 10k total lines
        num_files = 100
        lines_per_file = 100  # 10k total lines across 100 files
    else:
        num_files = args.files
        lines_per_file = args.lines_per_file

    # Open output
    if args.output:
        with open(args.output, "w") as f:
            print(f"Generating diff: {num_files} files, ~{lines_per_file} lines/file", file=sys.stderr)
            generate_large_diff(num_files, lines_per_file, f)
            print(f"Wrote {args.output}", file=sys.stderr)
    else:
        generate_large_diff(num_files, lines_per_file)


if __name__ == "__main__":
    main()
