"""
RacGoat Module Entry Point

Run with: python -m racgoat

This makes the package executable as a module - how 'goat' is that? 🐐
"""

import os
import sys
import signal
import subprocess
import tempfile
import selectors

from racgoat.cli.args import parse_arguments
from racgoat.main import main, run_tui
from racgoat.parser.diff_parser import parse_diff


def run() -> None:
    """
    Main entry point that handles both piped stdin and interactive mode.

    When stdin is piped (e.g., `git diff | racgoat`):
      - Writes stdin to a temp file
      - Spawns subprocess with stdin redirected to /dev/tty
      - Parent copies stdin data while child runs TUI

    When stdin is a tty (interactive):
      - Launches TUI directly in current process
    """
    stdin_tty = sys.__stdin__.isatty()

    # Parse arguments (both modes need -o flag)
    args = parse_arguments()

    # Check if we're the child process (have --diff-file from parent)
    if hasattr(args, 'diff_file') and args.diff_file:
        # Child process - parse diff file and launch TUI (Milestone 2)
        try:
            with open(args.diff_file, "r") as f:
                diff_input = f.read()
            diff_summary = parse_diff(diff_input.splitlines(keepends=True))
            run_tui(diff_summary, output_file=args.output)
        except (OSError, IOError):
            # Fallback to legacy mode on file read error
            main(diff_file=args.diff_file, output_file=args.output)
    elif stdin_tty:
        # Interactive mode - no diff, show empty state
        from racgoat.parser.models import DiffSummary
        run_tui(DiffSummary(files=[]), output_file=args.output)
    else:
        # Piped stdin mode - check if /dev/tty is available
        try:
            # Try to open /dev/tty - if this fails, we can't run TUI interactively
            with open("/dev/tty", "rb"):
                pass
            has_tty = True
        except (OSError, IOError):
            has_tty = False

        if not has_tty:
            # No /dev/tty available - parse stdin and launch TUI (Milestone 2)
            # This happens in environments like CI/CD or non-interactive shells
            stdin_data = sys.stdin.read()
            diff_summary = parse_diff(stdin_data.splitlines(keepends=True))
            run_tui(diff_summary, output_file=args.output)
        else:
            # /dev/tty available - use toolong pattern for proper interactive TUI
            def request_exit(*args_signal) -> None:
                """Handle interrupts gracefully."""
                sys.stderr.write("^C\n")

            signal.signal(signal.SIGINT, request_exit)
            signal.signal(signal.SIGTERM, request_exit)

            # Write piped data to temp file
            with tempfile.NamedTemporaryFile(
                mode="w+",
                delete=False,
                prefix="racgoat_",
                suffix=".diff"
            ) as temp_file:
                temp_path = temp_file.name

                try:
                    # Open /dev/tty for subprocess stdin
                    with open("/dev/tty", "rb", buffering=0) as tty_stdin:
                        # Launch subprocess to render TUI
                        process = subprocess.Popen(
                            [sys.executable, "-m", "racgoat", "-o", args.output, "--diff-file", temp_path],
                            stdin=tty_stdin,
                            close_fds=True,
                            env={**os.environ, "TEXTUAL_ALLOW_SIGNALS": "1"}
                        )

                        # Copy stdin to temp file while TUI runs
                        selector = selectors.SelectSelector()
                        selector.register(sys.stdin.fileno(), selectors.EVENT_READ)

                        while process.poll() is None:
                            for _, event in selector.select(0.1):
                                if process.poll() is not None:
                                    break
                                chunk = sys.stdin.read(8192)
                                if chunk:
                                    temp_file.write(chunk)
                                    temp_file.flush()
                                else:
                                    # EOF reached
                                    break

                        # Wait for process to complete
                        process.wait()

                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass


if __name__ == "__main__":
    run()
