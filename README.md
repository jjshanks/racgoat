# RacGoat 🦝🐐

**A TUI application that's part raccoon mischief, part goat stubbornness.**

RacGoat is a Python terminal user interface (TUI) built with [Textual](https://textual.textualize.io/), combining the clever resourcefulness of raccoons with the determined persistence of mountain goats.

---

## ✨ Features

- 🎨 Beautiful terminal UI powered by Textual
- 🦝 Raccoon-themed utility functions (because regular functions are boring)
- 🐐 Goat-level determination in climbing code mountains
- 🎭 Hidden easter eggs throughout the codebase
- 🧪 Comprehensive test suite (with puns!)
- 📚 Fun, personality-filled documentation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository (or you're already here!)
cd racgoat

# Install dependencies using UV
uv sync

# Run the application with a git diff
git diff | uv run python -m racgoat
```

That's it! The raccoon and goat are ready to help you review! 🦝🐐

---

## 🎮 Usage

RacGoat reads git diffs from stdin and displays a summary:

```bash
# Review staged changes
git diff --cached | uv run python -m racgoat

# Review unstaged changes
git diff | uv run python -m racgoat

# Review changes on a branch
git diff main...feature-branch | uv run python -m racgoat
```

Press `q` to quit the app.

---

## 📦 Project Structure

```
racgoat/
├── racgoat/              # Main application package
│   ├── __init__.py       # Package initialization with raccoon wisdom
│   ├── main.py           # Textual TUI application
│   └── utils.py          # Helper functions (goat_climb, raccoon_cache, etc.)
├── tests/                # Test suite with punny test names
│   └── test_goat.py      # "Trash panda meets cliff climber!"
├── docs/                 # Documentation
│   └── index.md          # Full documentation
├── pyproject.toml        # Project configuration (managed by UV)
├── README.md             # You are here! 📍
└── LICENSE               # MIT License
```

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_goat.py
```

Watch for the punny test names and hidden jokes! 🎭

---

## 🎨 Development

### Adding New Features

1. Create a new branch: `git checkout -b feature/amazing-raccoon-feature`
2. Make your changes (bonus points for animal puns!)
3. Write tests (make them funny!)
4. Run the test suite: `uv run pytest`
5. Submit a pull request

### Code Style

- Follow PEP 8 (but with more personality)
- Add animal-themed comments where appropriate
- Include puns in function docstrings
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
- [Full Documentation](docs/index.md)
- [Textual Documentation](https://textual.textualize.io/)
- [UV Documentation](https://docs.astral.sh/uv/)

---

## 🤝 Contributing

Contributions are welcome! Whether you're:
- 🦝 A raccoon finding bugs
- 🐐 A goat climbing to new features
- 🧑‍💻 A human writing code

We'd love your help! Please see the [documentation](docs/index.md) for contribution guidelines.

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

*"In code we trust, in raccoons we debug, in goats we climb."* - Ancient RacGoat Proverb

---

Made with 🦝 raccoon energy and 🐐 goat determination
