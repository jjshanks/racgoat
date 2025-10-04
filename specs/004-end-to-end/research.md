# Research: End-to-End Workflow & Markdown Output

**Date**: 2025-10-02
**Feature**: End-to-End Workflow & Markdown Output
**Branch**: 004-end-to-end

## Overview
This document captures research findings for implementing the comment serialization and Markdown output feature, including best practices for Textual modal dialogs, file I/O in Python, git metadata extraction, and Markdown formatting.

---

## Research Areas

### 1. Textual Modal Dialogs

**Decision**: Use Textual's built-in `Screen` with modal mode for error dialogs

**Rationale**:
- Textual 0.60.0+ supports modal screens via `push_screen_wait()` for blocking dialogs
- Modal screens overlay the main app without destroying state
- Keyboard navigation works out of the box (Enter/Escape)
- Screens can return values (user's choice: new path vs /tmp fallback)

**Implementation Pattern**:
```python
class ErrorRecoveryScreen(Screen):
    """Modal dialog for file write error recovery"""
    BINDINGS = [("escape", "dismiss", "Cancel")]

    def __init__(self, error_message: str):
        super().__init__()
        self.error_message = error_message

    def compose(self) -> ComposeResult:
        # Layout: message + buttons (new path, /tmp, cancel)
        pass

    def on_button_pressed(self, event) -> None:
        self.dismiss(result="new_path" | "/tmp" | None)

# Usage in main app:
result = await self.app.push_screen_wait(ErrorRecoveryScreen(error))
```

**Alternatives Considered**:
- Textual's legacy `Dialog` widget (deprecated in 0.60.0+)
- Custom overlay widget without Screen (more complex, breaks event flow)

**References**:
- Textual docs: Screens and modal behavior
- Existing RacGoat patterns: `RacGoatApp.action_quit()` in `main.py`

---

### 2. File I/O Best Practices (Python 3.12+)

**Decision**: Use `pathlib.Path` with exception handling and atomic writes

**Rationale**:
- `pathlib.Path` provides cross-platform path handling
- `Path.exists()` detects overwrite scenario (FR-002a)
- `Path.write_text()` handles encoding automatically (UTF-8 default)
- Atomic write pattern (write to temp, rename) prevents partial files on crash
- Context managers ensure file closure even on exceptions

**Implementation Pattern**:
```python
from pathlib import Path
import tempfile

def write_markdown_output(content: str, output_path: Path) -> None:
    """Write review output with atomic operation"""
    if output_path.exists():
        raise FileExistsError(f"Output file already exists: {output_path}")

    # Atomic write: temp file + rename
    temp_path = output_path.with_suffix('.tmp')
    try:
        temp_path.write_text(content, encoding='utf-8')
        temp_path.rename(output_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

**Alternatives Considered**:
- Direct `open()` calls (more verbose, no path manipulation helpers)
- `os.path` module (older API, less Pythonic)
- No atomic write (risk of partial file on crash)

**Edge Cases Handled**:
- Invalid path (OSError → modal dialog)
- No write permissions (PermissionError → modal dialog)
- Existing file (FileExistsError → modal dialog per FR-002a)
- Disk full (OSError → modal dialog)

---

### 3. Git Metadata Extraction

**Decision**: Use `subprocess` with `git` CLI commands

**Rationale**:
- Git CLI is universally available (RacGoat runs in git repositories)
- No external dependencies needed (avoids adding GitPython/Dulwich)
- Simple commands: `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`
- Graceful fallback when not in git repo (return placeholders per spec)

**Implementation Pattern**:
```python
import subprocess
from pathlib import Path

def get_git_metadata() -> tuple[str, str]:
    """Extract branch name and commit SHA, or return placeholders"""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2
        ).stdout.strip()

        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2
        ).stdout.strip()

        return (branch, sha)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ("Unknown Branch", "Unknown SHA")
```

**Alternatives Considered**:
- GitPython library (heavy dependency, 1MB+ install)
- Dulwich (pure Python git, but still 500KB+ dependency)
- Read `.git/HEAD` directly (fragile, breaks with detached HEAD or worktrees)

**Edge Cases Handled**:
- Not in a git repository (FileNotFoundError)
- Detached HEAD state (branch name shows commit SHA)
- Submodule or worktree (git commands work correctly)
- Git command timeout (2 second limit)

---

### 4. Markdown Formatting Standards

**Decision**: Use CommonMark-compliant Markdown with fenced code blocks

**Rationale**:
- CommonMark is widely supported (GitHub, GitLab, VSCode, etc.)
- Fenced code blocks (```) preserve diff syntax highlighting
- Heading hierarchy (H1 for title, H2 for sections, H3 for files)
- Preserve user Markdown (FR-010a: no escaping of *, #, [, etc.)

**Output Format**:
```markdown
# Code Review

**Branch**: main
**Commit**: a1b2c3d4

## File: path/to/file.py

### Line 42
Comment text here (user's Markdown preserved)

### Lines 50-55
Range comment text

## File: another/file.js

### File-level comment
Overall feedback about the file
```

**Alternatives Considered**:
- HTML output (less portable, harder to edit)
- Plain text (loses structure)
- JSON (not human-friendly for review documents)
- Escape all special chars (violates FR-010a, breaks user's intentional formatting)

**Edge Cases Handled**:
- User comment contains triple backticks (nested code blocks work in CommonMark)
- User comment contains heading markers (preserved as-is per FR-010a)
- File paths with spaces (no escaping needed in CommonMark)

---

### 5. Comment Data Model

**Decision**: Simple dataclass hierarchy with file-first organization

**Rationale**:
- Comments naturally group by file (matches review workflow)
- Three comment types: line, range, file-level (per Milestone 3 design)
- Dataclasses provide free `__repr__`, equality, and immutability
- Line numbers already tracked in `DiffHunk` model (reuse existing)

**Data Model**:
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Comment:
    """Base comment with text and position"""
    text: str
    comment_type: Literal["line", "range", "file"]

@dataclass(frozen=True)
class LineComment(Comment):
    line_number: int
    comment_type: Literal["line"] = "line"

@dataclass(frozen=True)
class RangeComment(Comment):
    start_line: int
    end_line: int
    comment_type: Literal["range"] = "range"

@dataclass(frozen=True)
class FileComment(Comment):
    comment_type: Literal["file"] = "file"

@dataclass
class FileReview:
    """All comments for a single file"""
    file_path: str
    comments: list[Comment]
```

**Alternatives Considered**:
- Flat comment list with file path in each comment (duplicates data, harder to group)
- Nested dict structure (no type safety, harder to test)
- Single Comment class with optional fields (ambiguous, harder to validate)

---

## Integration Points

### Existing Codebase
- `racgoat/main.py`: `action_quit()` method hooks for save logic
- `racgoat/cli/args.py`: Already has `-o` flag parsing (Milestone 1)
- `racgoat/parser/models.py`: `DiffFile` has file paths and line numbers
- `racgoat/ui/widgets/`: Can add modal dialog screen

### New Components Required
- `racgoat/models/comment.py`: Comment data model classes
- `racgoat/services/markdown_writer.py`: Serialization logic
- `racgoat/services/git_metadata.py`: Git extraction utility
- `racgoat/ui/widgets/error_dialog.py`: Modal error recovery screen
- `tests/contract/test_markdown_format.py`: Output format contract tests
- `tests/integration/test_end_to_end.py`: Full quit-and-save scenarios

---

## Performance Considerations

### Serialization Performance
- 100 comments @ ~100 chars each = ~10KB Markdown file
- String concatenation vs list join: Use list join for O(n) vs O(n²)
- File write <5 seconds target: 10KB write takes ~1ms on modern SSD
- Bottleneck is git subprocess calls (~50ms each)

**Optimization Strategy**:
- Use `str.join()` for Markdown assembly
- Call git commands once on quit (cache results)
- No lazy loading needed (100 comments is tiny dataset)

### TUI Responsiveness
- File write happens after quit initiated (user expects brief delay)
- Modal dialog blocks input (intended behavior)
- No risk of blocking main TUI loop (write is last action)

---

## Testing Strategy

### Contract Tests
- Markdown format validation (structure, headings, code blocks)
- Git metadata extraction (branch, SHA, fallback)
- File write atomic operation (temp file, rename)

### Integration Tests
- Quit with comments → file created with correct content
- Quit without comments → no file created
- Existing file → modal dialog → retry with new path
- Missing git → placeholders in output
- Special Markdown chars → preserved exactly

### Unit Tests
- Comment model serialization
- Path validation logic
- Error message formatting

---

## Open Questions

None - all clarifications resolved in spec Session 2025-10-02.

---

## References

1. Textual Documentation: https://textual.textualize.io/
   - Screens and modal behavior
   - Event handling patterns
2. Python `pathlib` docs: https://docs.python.org/3/library/pathlib.html
3. Git CLI reference: https://git-scm.com/docs
4. CommonMark Spec: https://commonmark.org/
5. RacGoat Constitution: `.specify/memory/constitution.md`
6. RacGoat PRD: `docs/prd.md`
7. Feature Spec: `specs/004-end-to-end/spec.md`

---

**Status**: Research complete ✅
**Next Phase**: Design & Contracts (Phase 1)
