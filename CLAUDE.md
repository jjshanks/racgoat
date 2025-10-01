# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RacGoat is a TUI (Terminal User Interface) application for reviewing AI-generated git diffs and creating structured feedback documents. Built with Textual framework and Python 3.12+, it combines a playful aesthetic (raccoon + goat theme) with practical code review functionality.

**Note:** The current codebase is a placeholder/demo. The actual application will be an AI code review tool per the PRD (see docs/prd.md).

## Development Commands

```bash
# Install dependencies
uv sync

# Run the application
uv run python -m racgoat

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_goat.py
```

## Architecture

### Core Components

**Entry Point:**
- `racgoat/__main__.py`: Module entry point, delegates to main()
- `racgoat/main.py`: Contains RacGoatApp (Textual App subclass)

**Current Implementation:**
- Single-screen TUI with Header, Footer, and centered Container
- CSS-based styling using Textual's styling system
- Keybindings: `q` to quit, easter egg activation via typing "trash"
- Event handlers: on_mount(), on_button_pressed(), on_key()

**Utilities:**
- `racgoat/utils.py`: Helper functions (goat_climb, raccoon_cache, etc.)
- All utilities follow the raccoon/goat theme with playful docstrings

### Planned Architecture (per PRD)

The application will evolve into a two-pane diff review tool:

1. **Input Layer:** Parse git diff from stdin, extract files/hunks/line numbers
2. **UI Layer:**
   - Left pane: File list navigation
   - Right pane: Diff display with syntax highlighting
   - Status bar: Context-sensitive help
3. **Comment System:** Line-level, range, and file-level comments with visual markers
4. **Output Layer:** Generate Markdown review files with branch/commit metadata

### Key Design Patterns

- **Textual Composition:** Uses `compose()` to build widget tree
- **Reactive Bindings:** BINDINGS class variable for keyboard shortcuts
- **CSS Styling:** CSS class variable for component styling
- **Event-Driven:** on_* methods handle UI events

## Implementation Guidelines

### Textual Framework Specifics

- Widgets are composed via `compose() -> ComposeResult`
- Use `query_one()` to access widgets by ID or type
- CSS uses Textual's custom properties ($primary, $accent, $warning, etc.)
- Keybindings defined as Binding tuples or (key, action, description) tuples
- Actions prefixed with "action_" (e.g., action_quit)

### Code Style

- Python 3.12+ features allowed
- Type hints encouraged (see utils.py examples)
- Docstrings follow Google style with playful tone
- Test names should be descriptive and follow the theme

### Testing

- pytest is the test framework
- Test file pattern: `test_*.py` in tests/
- Playful test names and docstrings are encouraged (see tests/test_goat.py)
- Run tests before committing changes

## PRD Implementation Roadmap

When implementing PRD features (docs/prd.md), follow the milestone sequence in docs/roadmap.md:

1. **Milestone 1 - CLI Data Processor & Parser:**
   - Read git diff from stdin
   - Parse diff to identify files and count added/removed lines
   - Filter binary/generated files (.lock, .min.js)
   - CLI argument parsing for `-o <filename>` flag
   - Output: Simple text summary to file (e.g., `path/to/file.py: +10 -5`)
   - Handle empty diff edge case

2. **Milestone 2 - TUI Rendering & Navigation:**
   - Build two-pane layout: Files Pane (left) + Diff Pane (right)
   - Populate file list from parsed data
   - Render diff hunks with ANSI color highlighting and post-change line numbers
   - Navigation: arrow keys (within pane), Tab (switch panes), q (quit)
   - Display "No diff" message for empty input

3. **Milestone 3 - Core Commenting Engine:**
   - Design in-memory data structures for comments
   - Implement single-line comment (a), file-level comment (c), range comments via Select Mode (s)
   - Display visual marker (*) in Diff Pane for comments
   - Context-sensitive status bar showing keybindings

4. **Milestone 4 - End-to-End Workflow & Markdown Output:**
   - Serialize comments to Markdown format on quit
   - Write to file specified by `-o` flag (default: review.md)
   - Skip output if no comments exist
   - Include branch name and commit SHA in output header

5. **Milestone 5 - Advanced Interaction & Usability:**
   - Comment edit/delete functionality (e)
   - Search functionality (/) within diff view
   - Help overlay (?) displaying all keybindings

6. **Milestone 6 - Performance Hardening & Final Polish:**
   - Lazy loading and viewport rendering for 100 files / 10k lines
   - Benchmark against large real-world diffs
   - Robust error handling for malformed diffs
   - UI refinement for clarity and consistency

Key PRD constraints:
- Support up to 100 files and 10k diff lines
- Skip binary/generated files (.lock, .min.js, etc.)
- Post-change line numbers with +/- prefixes
- One comment per line/range, overlaps allowed
- Output only if comments exist

## Package Management

- Uses UV for dependency management (not pip/poetry)
- pyproject.toml uses hatchling as build backend
- Python >=3.12 required (set in .python-version)
- Add dependencies via `uv add <package>`
- Add dev dependencies via `uv add --dev <package>`
