"""CLI main entry point for diff processing."""

import sys

from racgoat.cli.args import parse_arguments
from racgoat.parser.diff_parser import parse_diff


def main():
    """Main entry point for the CLI diff processor.

    Reads git diff from stdin, parses it, filters binary/generated files,
    and writes a summary to the specified output file.

    Exit codes:
        0: Success (including empty diff)
        1: Error (invalid arguments, file write errors, etc.)
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Read diff from stdin
        stdin_lines = sys.stdin.readlines()

        # Parse the diff
        summary = parse_diff(stdin_lines)

        # Only write output if there are files to report
        if not summary.is_empty:
            with open(args.output, 'w') as f:
                f.write(summary.format_output())

        # Exit successfully
        sys.exit(0)

    except Exception as e:
        # Print error to stderr and exit with error code
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
