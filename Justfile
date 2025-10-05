# RacGoat Justfile
# Command runner for the raccoon-goat diff review TUI
# Run `just` or `just --list` to see all available recipes

# Default recipe: show available commands
default:
    @just --list

# Install dependencies with uv
install:
    uv sync

# Run racgoat TUI (pipe a diff file or use stdin)
# Usage: just run [diff_file] [output_file]
# Examples:
#   just run sample.diff review.md
#   git diff | just run
run diff_file="" output_file="review.md":
    #!/usr/bin/env bash
    if [ -n "{{diff_file}}" ]; then
        uv run python -m racgoat -o {{output_file}} < {{diff_file}}
    else
        uv run python -m racgoat -o {{output_file}}
    fi

# Quick demo: generate a sample diff and run racgoat
demo:
    @echo "🦝 Generating sample diff..."
    @just gen-small demo.diff
    @echo "🐐 Launching RacGoat TUI..."
    @just run demo.diff demo_review.md
    @echo "✨ Demo complete! Output: demo_review.md"

# Run all tests
test:
    uv run pytest

# Run all tests with verbose output
test-verbose:
    uv run pytest -v

# Run unit tests only
test-unit:
    uv run pytest tests/unit/ -v

# Run integration tests only
test-integration:
    uv run pytest tests/integration/ -v

# Run contract tests (validates PRD requirements)
test-contract:
    uv run pytest tests/contract/ -v

# Run performance tests
test-performance:
    uv run pytest tests/integration/test_performance/ -v

# Run tests for a specific milestone
# Usage: just test-milestone 2
test-milestone milestone:
    uv run pytest tests/integration/test_milestone{{milestone}}/ -v

# Run tests with coverage report
test-coverage:
    uv run pytest --cov=racgoat --cov-report=html --cov-report=term

# Run tests in watch mode (re-run on file changes)
test-watch:
    uv run pytest-watch

# Generate a test diff file
# Usage: just gen-diff [preset] [output_file]
# Presets: small, medium, large, max
gen-diff preset="medium" output="test.diff":
    uv run python scripts/generate_large_diff.py --preset {{preset}} -o {{output}}

# Generate small test diff (10 files, 50 lines/file)
gen-small output="small.diff":
    @just gen-diff small {{output}}

# Generate medium test diff (50 files, 100 lines/file)
gen-medium output="medium.diff":
    @just gen-diff medium {{output}}

# Generate large test diff (100 files, 100 lines/file)
gen-large output="large.diff":
    @just gen-diff large {{output}}

# Generate max test diff (100 files, 100 lines/file = ~10k lines)
gen-max output="max.diff":
    @just gen-diff max {{output}}

# Clean Python cache files and test artifacts
clean:
    #!/usr/bin/env bash
    echo "🧹 Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    echo "✨ Clean complete!"

# Run quick checks (tests + any linters)
check: test
    @echo "✅ All checks passed!"

# Show project info and status
info:
    @echo "🦝🐐 RacGoat - Terminal Diff Review TUI"
    @echo ""
    @echo "Python version:"
    @python --version
    @echo ""
    @echo "UV version:"
    @uv --version
    @echo ""
    @echo "Git status:"
    @git status --short
    @echo ""
    @echo "Project version:"
    @grep '^version = ' pyproject.toml

# Bootstrap development environment (install + run tests)
bootstrap: install test
    @echo "🎉 Bootstrap complete! Ready to climb and cache!"
