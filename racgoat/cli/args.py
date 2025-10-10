"""CLI argument parsing."""

import argparse

from racgoat import __version__


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the diff processor.

    Returns:
        argparse.Namespace with parsed arguments including:
            - output: Output file path (default: 'review.md')
            - diff_file: Internal flag for passing temp file from parent process

    Raises:
        SystemExit: If invalid arguments provided (via argparse).
    """
    parser = argparse.ArgumentParser(
        description="Parse git diff and generate summary",
        prog="racgoat"
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '-o', '--output',
        default='review.md',
        help='Output file path (default: review.md)'
    )
    parser.add_argument(
        '-s', '--staged',
        action='store_true',
        help='Run git diff --staged in current directory (when no input is piped)'
    )
    parser.add_argument(
        '--diff-file',
        dest='diff_file',
        help=argparse.SUPPRESS  # Hidden internal argument
    )
    return parser.parse_args()
