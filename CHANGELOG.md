# Changelog

All notable changes to RacGoat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-05 - "The Champion of Syntaxia" 🦝🐐

### 🎉 Initial Release

RacGoat v1.0.0 is a fully-featured TUI application for reviewing git diffs with structured commenting and Markdown output. Built through 7 development milestones over several iterations.

### ✨ Features

#### Core Functionality
- **Interactive Diff Review**: Two-pane TUI with file list and syntax-highlighted diff display
- **Structured Commenting System**:
  - Line-level comments (`c` key)
  - Range comments via Select Mode (`s` key)
  - File-level comments (`Shift+C` key)
  - Edit/delete existing comments (`e` key)
- **Search Functionality**:
  - Search within diffs (`/` key)
  - Case-sensitive literal matching
  - Next/previous navigation (`n`/`N` keys)
  - Visual highlighting of matches
- **Markdown Output**:
  - Structured review documents
  - YAML frontmatter with metadata
  - Machine-readable comment metadata (HTML comments)
  - Code context blocks with line numbers
  - Git branch and commit SHA tracking
- **Help System**: Built-in help overlay (`?` key) with all keybindings

#### User Experience
- **Keyboard-Driven Navigation**:
  - Arrow keys for file list navigation and diff scrolling
  - Tab to cycle focus between panes
  - `q` to quit and save review
- **Visual Feedback**:
  - ANSI syntax highlighting for diff content
  - Comment markers (`*`) in diff view
  - Context-sensitive status bar
  - Distinct highlighting for current search match
- **Performance**:
  - Handles up to 100 files / 10,000 lines
  - <2s load time for maximum-size diffs
  - <200ms for all UI operations
  - Viewport rendering for efficient scrolling
- **Robust Error Handling**:
  - Graceful handling of malformed diff hunks
  - Size limit enforcement with user-friendly error modal
  - Atomic file writes to prevent corruption
  - File write error recovery

#### Developer Experience
- **Comprehensive Test Suite**:
  - 146+ tests across contract, integration, and unit categories
  - Performance benchmarks
  - Contract tests validating all PRD requirements
- **Well-Documented Codebase**:
  - Playful, animal-themed docstrings
  - Architecture documentation in CLAUDE.md
  - Feature specifications in specs/ directory
- **Development Tools**:
  - Justfile with common development commands
  - Test data generator for performance testing
  - UV-based dependency management

### 🎨 Design Philosophy

- **Raccoon Energy**: Clever, resourceful, finding treasure in messy diffs
- **Goat Determination**: Persistent, sure-footed navigation through complex changes
- **Playful Theme**: Animal-themed messages, puns in docstrings, hidden easter eggs

### 📦 Installation

```bash
# Install from PyPI
uv tool install racgoat

# Or install from GitHub
uv tool install git+https://github.com/jjshanks/racgoat.git
```

### 🚀 Quick Start

```bash
# Review unstaged changes
git diff | racgoat

# Review and save to file
git diff --cached | racgoat -o review.md

# Review specific commits
git diff HEAD~1 | racgoat
```

### 🔧 Technical Details

**Requirements:**
- Python 3.12 or higher
- Textual framework 6.2.0+
- UV package manager (recommended)

**Supported Platforms:**
- Linux
- macOS
- Windows (via WSL recommended)

**Binary File Filtering:**
Automatically excludes binary files and common generated files:
- `.lock` files (package-lock.json, Cargo.lock, etc.)
- `.min.js`, `.min.css` minified files
- `.map` source maps
- Image files (.png, .jpg, .gif, etc.)
- Binary executables

### 📊 Development Milestones

This release represents the completion of 7 major milestones:

1. **Milestone 1 - CLI Data Processor & Parser**
   - Git diff parsing from stdin
   - File and hunk extraction
   - Binary/generated file filtering
   - CLI argument parsing

2. **Milestone 2 - TUI Rendering & Navigation**
   - Two-pane layout (Files + Diff)
   - Syntax highlighting
   - Keyboard navigation
   - Tab focus cycling

3. **Milestone 3 - Core Commenting Engine**
   - In-memory comment storage
   - Line, range, and file-level comments
   - Visual markers in diff view
   - Select Mode for ranges

4. **Milestone 4 - End-to-End Workflow & Markdown Output**
   - Comment serialization to Markdown
   - Git metadata extraction
   - File output with error recovery
   - Atomic writes

5. **Milestone 5 - Advanced Interaction & Usability**
   - Comment edit/delete functionality
   - Search with navigation and highlighting
   - Help overlay
   - Context-sensitive UI

6. **Milestone 6 - Performance Hardening & Final Polish**
   - Parser error handling
   - Size limit enforcement
   - Viewport rendering optimization
   - Performance benchmarks

7. **Milestone 7 - Enhanced Markdown Output Format**
   - YAML frontmatter with metadata
   - HTML comment annotations
   - Code context blocks
   - Machine-readable format for AI agents

### 🐛 Known Limitations

- Maximum supported diff size: 100 files or 10,000 total lines
- Binary files are filtered out (shown in file count but not in list)
- Overlapping range comments are allowed but may create ambiguous output
- Requires terminal with ANSI color support for best experience

### 🙏 Acknowledgments

- [Textual](https://textual.textualize.io/) team for the excellent TUI framework
- [UV](https://github.com/astral-sh/uv) team for fast Python package management
- All raccoons and goats for inspiration 🦝🐐

### 📝 Notes

This is the first stable release of RacGoat. All core features are complete and thoroughly tested. Future releases will focus on:
- Additional export formats
- Lazy loading for very large diffs
- Plugin system for custom workflows
- Integration with AI code review tools

---

**Full Changelog**: https://github.com/jjshanks/racgoat/commits/v1.0.0

## [Unreleased]

Nothing yet! Stay tuned for future updates.

---

*"In code we trust, in raccoons we debug, in goats we climb."* - Ancient RacGoat Proverb 🦝🐐
