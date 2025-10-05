# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RacGoat is a TUI (Terminal User Interface) application for reviewing AI-generated git diffs and creating structured feedback documents. Built with Textual framework and Python 3.12+, it combines a playful aesthetic (raccoon + goat theme) with practical code review functionality.

**Note:** The current codebase is a placeholder/demo. The actual application will be an AI code review tool per the PRD (see docs/prd.md).

## Development Commands

```bash
# Install dependencies
uv sync

# Run the application (Milestone 2: TUI mode)
uv run python -m racgoat < /path/to/diff.diff

# Generate test diffs for performance testing
uv run python scripts/generate_large_diff.py --preset max -o large.diff

# Run the TUI with generated diff
uv run python -m racgoat < large.diff

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run Milestone 2 integration tests
uv run pytest tests/integration/test_milestone2/ -v

# Run parser tests (Milestone 1)
uv run pytest tests/unit/test_diff_parser.py -v
```

## Quick Start (Milestone 2)

```bash
# Generate a sample diff
git diff HEAD~1 > sample.diff

# Launch TUI to review the diff
uv run python -m racgoat < sample.diff

# Navigation:
# - Arrow keys: Navigate file list
# - q: Quit application
# - First file is auto-selected on launch
```

## Architecture

### Core Components

**Entry Point:**
- `racgoat/__main__.py`: Module entry point, delegates to main()
- `racgoat/main.py`: Contains RacGoatApp (Textual App subclass)

**Current Implementation (Milestone 2):**
- Two-pane TUI with Header, Footer, and TwoPaneLayout
- CSS-based styling using Textual's styling system
- Keybindings: `q` to quit, arrow keys for navigation
- Event-driven architecture with FileSelected messages

**Widgets (racgoat/ui/widgets/):**
- `FilesPane`: Scrollable file list with selection (extends VerticalScroll, contains ListView)
- `DiffPane`: Diff display with Rich Text syntax highlighting (extends Static)
- `TwoPaneLayout`: Container managing both panes (extends Horizontal)

**Models:**
- **Parser models** (racgoat/parser/models.py):
  - `DiffHunk`: Represents a contiguous block of changes with line-level detail
  - `DiffFile`: File metadata with hunks list
  - `DiffSummary`: Container for all files in a diff
- **UI models** (racgoat/ui/models.py):
  - `FilesListItem`: UI model for formatted file list entries
  - `PaneFocusState`: Enum for tracking which pane has focus
- **Comment models** (racgoat/models/comments.py):
  - Milestone 3: `Comment`, `CommentTarget`, `CommentType` (for UI/storage)
  - Milestone 4: `SerializableComment`, `LineComment`, `RangeComment`, `FileComment`, `FileReview`, `ReviewSession` (for Markdown serialization)

**Services:**
- `racgoat/services/comment_store.py`: In-memory comment storage (Milestone 3)
- `racgoat/services/markdown_writer.py`: Markdown serialization and file writing (Milestone 4)
- `racgoat/services/git_metadata.py`: Git branch/SHA extraction (Milestone 4)

**Utilities:**
- `racgoat/utils.py`: Helper functions (goat_climb, raccoon_cache, etc.)
- All utilities follow the raccoon/goat theme with playful docstrings

### Current Architecture (Milestone 2 Complete)

The application is now a functional two-pane diff review tool:

1. **Input Layer (✅ Complete):**
   - Parse git diff from stdin with hunk-level detail
   - Extract files, hunks, line numbers, and change types
   - Filter binary and generated files

2. **UI Layer (✅ Milestone 2 Complete):**
   - Left pane: FilesPane with file list navigation (30% width)
   - Right pane: DiffPane with syntax-highlighted diff display (70% width)
   - Arrow keys navigate file list
   - Auto-select first file on launch
   - Empty diff shows friendly message

3. **Comment System (🔜 Milestone 3):** Line-level, range, and file-level comments with visual markers

4. **Output Layer (🔜 Milestone 4):** Generate Markdown review files with branch/commit metadata

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

1. **Milestone 1 - CLI Data Processor & Parser (✅ COMPLETE):**
   - ✅ Read git diff from stdin
   - ✅ Parse diff to identify files and count added/removed lines
   - ✅ Filter binary/generated files (.lock, .min.js)
   - ✅ CLI argument parsing for `-o <filename>` flag
   - ✅ Output: Simple text summary to file (e.g., `path/to/file.py: +10 -5`)
   - ✅ Handle empty diff edge case
   - ✅ All 13 parser tests passing

2. **Milestone 2 - TUI Rendering & Navigation (✅ COMPLETE):**
   - ✅ Build two-pane layout: Files Pane (left) + Diff Pane (right)
   - ✅ Populate file list from parsed data
   - ✅ Render diff hunks with ANSI color highlighting and post-change line numbers
   - ✅ Navigation: arrow keys navigate file list, Tab cycles focus, q quits
   - ✅ Display "No diff" message for empty input
   - ✅ Extended parser with DiffHunk model for line-level detail
   - ✅ Created FilesPane, DiffPane, TwoPaneLayout widgets
   - ✅ **All 57 tests passing** (33 contract + 11 integration + 13 parser tests)
   - ✅ Tab focus cycling fully functional (files ↔ diff pane)
   - ✅ Performance: Handles 20+ files with 2000+ lines, all operations < 200ms
   - 📊 Test coverage: Edge cases, rendering, navigation, performance all validated

3. **Milestone 3 - Core Commenting Engine (✅ COMPLETE):**
   - ✅ Design in-memory data structures for comments
   - ✅ Implement single-line comment (a), file-level comment (c), range comments via Select Mode (s)
   - ✅ Display visual marker (*) in Diff Pane for comments
   - ✅ Context-sensitive status bar showing keybindings

4. **Milestone 4 - End-to-End Workflow & Markdown Output (✅ COMPLETE):**
   - ✅ Serialize comments to Markdown format on quit
   - ✅ Write to file specified by `-o` flag (default: review.md)
   - ✅ Skip output if no comments exist
   - ✅ Include branch name and commit SHA in output header
   - ✅ Error recovery modal for file write failures
   - ✅ Atomic file write (temp + rename) to prevent corruption
   - ✅ Git metadata extraction with fallback placeholders
   - ✅ **All 30 M4 tests passing** (6 contract + 7 integration + 12 unit + 2 performance + 3 git)
   - 📊 Total test count: **87 tests** (57 from M1-M2 + 30 from M4)
   - ✅ Performance validated: 100 comments serialize <5s, file write <1s

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
