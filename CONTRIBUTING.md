# Contributing to RacGoat 🦝🐐

First off, thank you for considering contributing to RacGoat! Whether you're a raccoon finding bugs or a goat climbing to new features, we appreciate your help!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project follows a simple code of conduct: Be kind, be respectful, and have fun! We're building a tool with personality, so bring your creativity and sense of humor.

## Getting Started

Before you begin:
- Make sure you have Python 3.12 or higher installed
- Install [UV](https://github.com/astral-sh/uv) package manager
- Familiarize yourself with [Textual](https://textual.textualize.io/) if you'll be working on the UI

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/racgoat.git
cd racgoat
```

2. **Install dependencies**

```bash
# Using Just (recommended)
just install

# Or manually
uv sync
```

3. **Verify installation**

```bash
# Run tests
just test

# Or manually
uv run pytest

# Try running the app
echo "test" | uv run python -m racgoat
```

## Making Changes

### Branch Naming

Create a descriptive branch name:
- `feature/amazing-raccoon-feature` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/component-name` - Code refactoring

### Development Workflow

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for your changes
4. Run the test suite: `just test`
5. Commit your changes (see commit guidelines below)
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a Pull Request

### Commit Messages

We follow conventional commit format (but with more personality):

```
feat: add raccoon mode for enhanced trash detection
fix: goat now climbs steeper cliffs without falling
docs: update README with more animal puns
test: add test for the elusive mountain goat edge case
refactor: organize raccoon utilities into separate module
```

## Testing

RacGoat has a comprehensive test suite organized into three categories:

### Running Tests

```bash
# Run all tests
just test

# Run specific test categories
just test-unit          # Unit tests only
just test-integration   # Integration tests only
just test-contract      # Contract tests (PRD requirements)

# Run with verbose output
just test-verbose

# Run specific test file
uv run pytest tests/unit/test_diff_parser.py -v
```

### Test Categories

- **Contract tests** (`tests/contract/`): Validate PRD requirements
- **Integration tests** (`tests/integration/`): End-to-end TUI workflows
- **Unit tests** (`tests/unit/`): Individual component tests

### Writing Tests

- Use descriptive test names (puns encouraged!)
- Follow the existing test structure
- Test both happy paths and edge cases
- Include docstrings with playful descriptions
- Aim for high coverage of new code

Example:

```python
def test_raccoon_finds_treasure_in_garbage():
    """The raccoon's keen eye spots valuable data in messy diffs.

    This test verifies that our raccoon can parse through
    chaotic diffs and extract the good stuff!
    """
    diff = create_messy_diff()
    result = raccoon_parse(diff)
    assert result.treasure_count > 0
```

### Generating Test Data

For performance testing:

```bash
# Generate test diffs of various sizes
just gen-small    # 10 files, 50 lines/file
just gen-medium   # 50 files, 100 lines/file
just gen-large    # 100 files, 100 lines/file
just gen-max      # Maximum size (10k lines)
```

## Code Style

### Python Style Guidelines

- Follow PEP 8 (but with personality!)
- Use type hints for all function signatures
- Python 3.12+ features are allowed and encouraged
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names (bonus points for animal-themed names)

### Documentation

- All public functions/classes need docstrings
- Use Google-style docstrings
- Include examples where helpful
- Playful tone is encouraged (see existing code for examples)

Example:

```python
def goat_climb(path: str, difficulty: int = 5) -> bool:
    """Climb to new heights with the determination of a mountain goat.

    This function attempts to navigate complex file paths with the
    sure-footedness of our hoofed friends.

    Args:
        path: The treacherous path to climb
        difficulty: How steep the climb (1-10, default: 5)

    Returns:
        True if the summit was reached, False if we slipped

    Example:
        >>> goat_climb("/mountain/peak/treasure.txt")
        True  # Made it to the top!
    """
    # Implementation here
```

### Project Architecture

When adding new features, follow the existing architecture:

```
racgoat/
├── parser/         # Diff parsing logic
├── ui/             # TUI widgets and components
│   └── widgets/    # Individual UI widgets
├── services/       # Business logic (comment store, markdown writer)
├── models/         # Domain models
└── cli/            # CLI argument parsing
```

See `CLAUDE.md` for detailed architecture documentation.

## Submitting Changes

### Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Add tests** for new features
3. **Run the full test suite** and ensure all tests pass
4. **Update CHANGELOG.md** with a description of your changes
5. **Write a clear PR description**:
   - What problem does this solve?
   - How does it work?
   - Any breaking changes?
   - Screenshots/demos for UI changes

### PR Title Format

```
feat: add search functionality with regex support
fix: resolve issue with binary file filtering
docs: improve installation instructions
```

### Review Process

- Maintainers will review your PR
- Address any feedback promptly
- Be patient - we're all volunteers here!
- Keep discussions respectful and constructive

## Reporting Bugs

Found a bug? Help us squash it!

### Before Submitting

- Check existing issues to avoid duplicates
- Verify the bug exists in the latest version
- Collect information about your environment

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Run command X
2. Do action Y
3. See error Z

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 24.04]
- Python version: [e.g., 3.12.0]
- RacGoat version: [e.g., 1.0.0]
- Terminal: [e.g., Alacritty, iTerm2]

**Additional Context**
Any other relevant information
```

## Suggesting Features

Have an idea for a new feature? We'd love to hear it!

### Feature Request Template

```markdown
**Feature Description**
What feature would you like to see?

**Use Case**
Why would this be useful?

**Proposed Solution**
How do you envision this working?

**Alternatives Considered**
Any alternative approaches?

**Additional Context**
Mockups, examples, or other context
```

## Development Tips

### Using Just

We use [Just](https://github.com/casey/just) as a command runner:

```bash
just          # List all commands
just install  # Install dependencies
just test     # Run all tests
just clean    # Clean up build artifacts
just demo     # Run a quick demo
```

See `Justfile` for all available commands.

### Quick Development Loop

```bash
# Make changes to code
vim racgoat/ui/widgets/diff_pane.py

# Run relevant tests
just test-integration

# Try it out manually
git diff | uv run python -m racgoat

# Run full test suite before committing
just test
```

### Debugging Tips

- Use Textual's built-in developer tools: `textual console` in one terminal
- Add `self.log("Debug message")` in Textual widgets
- Use `pytest -vv` for very verbose test output
- Check `tests/integration/` for examples of testing TUI components

## Easter Eggs

Feel free to add easter eggs to your contributions! We love surprises for curious users. Just make sure they're:
- Fun and harmless
- Don't interfere with core functionality
- Document them in comments (so future maintainers don't remove them by accident!)

## Questions?

- Check the [documentation](https://github.com/jjshanks/racgoat#readme)
- Read the [CLAUDE.md](CLAUDE.md) file for architecture details
- Open an issue with the `question` label
- Review existing code for examples

## Recognition

Contributors will be recognized in:
- The project README
- Release notes for their contributions
- Our eternal gratitude! 🦝🐐

---

*"Don't be a scapegoat - ask for help if you need it!"* 🐐

*"Channel your inner raccoon - be curious, be creative, be persistent!"* 🦝

---

Thank you for contributing to RacGoat! May your code be bug-free and your commits be clean. 🎉
