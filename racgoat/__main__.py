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
from racgoat.main import main


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
        # Child process - launch TUI with diff file
        main(diff_file=args.diff_file, output_file=args.output)
    elif stdin_tty:
        # Interactive mode - launch TUI directly
        main(diff_file=None, output_file=args.output)
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
            # No /dev/tty available - write stdin to temp file and launch TUI non-interactively
            # This happens in environments like CI/CD or non-interactive shells
            with tempfile.NamedTemporaryFile(
                mode="w+",
                delete=False,
                prefix="racgoat_",
                suffix=".diff"
            ) as temp_file:
                temp_path = temp_file.name
                # Read all stdin
                stdin_data = sys.stdin.read()
                temp_file.write(stdin_data)
                temp_file.flush()

            try:
                # Launch TUI with the temp file
                main(diff_file=temp_path, output_file=args.output)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
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
