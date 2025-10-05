# RacGoat 🦝🐐

![RacGoat Demo](demo/racgoat-demo.gif)

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**A TUI application for reviewing AI-generated git diffs - part raccoon mischief, part goat stubbornness.**

RacGoat is a terminal user interface (TUI) that helps you efficiently review AI-generated code changes and create structured feedback documents. Built with [Textual](https://textual.textualize.io/) and Python 3.12+, it combines the clever resourcefulness of raccoons with the determined persistence of mountain goats.

---

## ✨ Features

### Core Functionality

- 📝 **Interactive Diff Review**: Two-pane TUI with file list and syntax-highlighted diff view
- 💬 **Structured Comments**: Add line-level, range, and file-level review comments
- 🔍 **Search & Navigate**: Search within diffs with match highlighting and navigation
- 📄 **Markdown Output**: Export review comments to structured Markdown files
- ⚡ **Performance**: Handles up to 100 files / 10,000 lines with <2s load time
- 🛡️ **Robust Error Handling**: Graceful handling of malformed hunks and oversized diffs

### User Experience

- ⌨️ **Keyboard-Driven**: Full keyboard navigation (no mouse required)
- 🎨 **Syntax Highlighting**: ANSI color highlighting for diff content
- ❓ **Built-in Help**: Press `?` to see all keybindings
- ✏️ **Edit/Delete Comments**: Modify comments before finalizing review
- 🦝🐐 **Playful Theme**: Raccoon and goat themed messages and easter eggs
- 🧪 **Well-Tested**: 42+ contract tests ensuring reliability

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Installation

**Option 1: Install from GitHub (recommended)**

```bash
# Using uv (fastest)
uv tool install git+https://github.com/jjshanks/racgoat.git

# Or using pipx
pipx install git+https://github.com/jjshanks/racgoat.git

# Or using pip
pip install git+https://github.com/jjshanks/racgoat.git
```

**Option 2: Development install**

```bash
# Clone the repository
git clone https://github.com/jjshanks/racgoat.git
cd racgoat

# Install dependencies (creates virtual environment)
uv sync

# The package is now available via `uv run`
```

That's it! The raccoon and goat are ready to help you review! 🦝🐐

---

## 🎮 Usage

### Basic Usage

RacGoat reads git diffs from stdin and opens an interactive TUI:

```bash
# Review unstaged changes
git diff | racgoat

# Review staged changes and save to file
git diff --cached | racgoat -o review.md

# Review changes on a branch
git diff main...feature-branch | racgoat

# Review specific commits
git diff HEAD~1 | racgoat
```

**Development mode:** If you're working on RacGoat itself, use `uv run python -m racgoat` instead.

**Uninstalling:**

```bash
# If installed via uv tool
uv tool uninstall racgoat

# If installed via pip
uv pip uninstall racgoat
```

### Keybindings

**Navigation:**

- `↑/↓` - Navigate file list or scroll diff
- `Tab` - Switch focus between Files Pane and Diff Pane
- `q` - Quit and save review to file

**Commenting:**

- `c` - Add line comment at cursor
- `s` - Enter Select Mode to create range comment
- `Shift+C` - Add file-level comment
- `e` - Edit or delete existing comment

**Search:**

- `/` - Enter search mode
- `Enter` - Execute search
- `n` - Jump to next match
- `N` - Jump to previous match (Shift+n)
- `Esc` - Exit search mode and clear highlights

**Help:**

- `?` - Show/hide help overlay with all keybindings

---

## 📦 Project Structure

```
racgoat/
├── racgoat/                    # Main application package
│   ├── __main__.py             # Entry point
│   ├── main.py                 # RacGoatApp (Textual app)
│   ├── parser/                 # Diff parsing
│   │   ├── diff_parser.py      # Git diff parser
│   │   └── models.py           # DiffHunk, DiffFile, DiffSummary
│   ├── ui/                     # TUI widgets
│   │   ├── widgets/            # FilesPane, DiffPane, StatusBar, etc.
│   │   └── models.py           # UI state models
│   ├── services/               # Business logic
│   │   ├── comment_store.py    # In-memory comment storage
│   │   ├── markdown_writer.py  # Review output generator
│   │   └── git_metadata.py     # Git branch/SHA extraction
│   ├── models/                 # Domain models
│   │   └── comments.py         # Comment types and serialization
│   ├── exceptions.py           # Custom exceptions
│   └── utils.py                # Helper functions
├── tests/                      # Test suite
│   ├── contract/               # Contract tests (PRD requirements)
│   ├── integration/            # End-to-end TUI tests
│   └── unit/                   # Unit tests
├── specs/                      # Feature specifications (Milestone 1-6)
├── scripts/                    # Development scripts
│   └── generate_large_diff.py  # Performance test data generator
├── docs/                       # Documentation
├── CLAUDE.md                   # AI coding assistant context
├── pyproject.toml              # Project configuration (UV)
└── README.md                   # You are here! 📍
```

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test categories
uv run pytest tests/contract/        # Contract tests (PRD requirements)
uv run pytest tests/integration/     # Integration tests (TUI workflows)
uv run pytest tests/unit/            # Unit tests (parser, models)

# Run performance tests
uv run pytest tests/integration/test_performance/ -v

# Run specific test file
uv run pytest tests/contract/test_error_handling.py -v
```

**Test Status (Milestone 6):**

- ✅ 42/42 core contract tests passing
- ✅ Parser, edit, search, and help features fully tested
- ⚠️ Performance and UI consistency tests need cleanup

Watch for the punny test names and hidden jokes! 🎭

---

## 🎨 Development

### Development Milestones

RacGoat is developed through structured milestones (see `specs/` directory):

- ✅ **Milestone 1**: CLI Data Processor & Parser
- ✅ **Milestone 2**: TUI Rendering & Navigation
- ✅ **Milestone 3**: Core Commenting Engine
- ✅ **Milestone 4**: End-to-End Workflow & Markdown Output
- ✅ **Milestone 5**: Advanced Interaction & Usability (Edit, Search, Help)
- 🔄 **Milestone 6**: Performance Hardening & Final Polish (Core complete)

### Adding New Features

1. Create a new branch: `git checkout -b feature/amazing-raccoon-feature`
2. Make your changes (bonus points for animal puns!)
3. Write tests (make them funny!)
4. Run the test suite: `uv run pytest`
5. Submit a pull request

### Code Style

- Follow PEP 8 (but with more personality)
- Use type hints (Python 3.12+ features allowed)
- Add animal-themed comments where appropriate
- Include puns in function docstrings
- See `CLAUDE.md` for detailed architecture guidelines
- Don't be a scapegoat - ask for help! 🐐

---

## 🥚 Easter Eggs

There are several easter eggs hidden in the codebase! We won't spoil all of them, but here are some hints:

- 🦝 Try typing something related to raccoons in the app...
- 👀 Check the comments in the test files
- 🧙 Look for hidden wisdom in the package initialization
- 🎨 ASCII art might be lurking somewhere...

Happy hunting! The most curious raccoons and determined goats will find them all.

---

## 📚 Documentation

For more detailed documentation, check out:

- **[CLAUDE.md](CLAUDE.md)** - Architecture, development commands, and PRD roadmap
- **[specs/](specs/)** - Feature specifications for each milestone
- **[docs/prd.md](docs/prd.md)** - Product Requirements Document
- [Textual Documentation](https://textual.textualize.io/) - TUI framework
- [UV Documentation](https://docs.astral.sh/uv/) - Package manager

---

## 🤝 Contributing

Contributions are welcome! Whether you're:

- 🦝 A raccoon finding bugs
- 🐐 A goat climbing to new features
- 🧑‍💻 A human writing code

We'd love your help! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines, development setup, and coding standards.

---

## 📄 License

MIT License - Free as a goat on a mountain or a raccoon in the night!

See [LICENSE](LICENSE) for full details.

---

## 🙏 Acknowledgments

- The [Textual](https://textual.textualize.io/) team for making TUIs beautiful
- The [UV](https://github.com/astral-sh/uv) team for lightning-fast Python package management
- Raccoons everywhere for teaching us to be resourceful
- Goats everywhere for teaching us to never give up
- You, for checking out this project! 🎉

---

## 💬 Support

Found a bug? Have a question? Want to share a raccoon or goat pun?

- Open an issue on GitHub
- Check the [documentation](docs/index.md)
- Or just enjoy the app! 🦝🐐

---

_"In code we trust, in raccoons we debug, in goats we climb."_ - Ancient RacGoat Proverb

---

Made with 🦝 raccoon energy and 🐐 goat determination
