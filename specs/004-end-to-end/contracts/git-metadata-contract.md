# Git Metadata Extraction Contract

**Feature**: End-to-End Workflow & Markdown Output
**Contract Type**: Service Interface Specification
**Version**: 1.0.0
**Date**: 2025-10-02

---

## Purpose

This contract defines the interface for extracting git repository metadata (branch name and commit SHA) used in review output headers. Contract tests verify correct behavior in all git repository states.

---

## Interface Specification

### Function Signature

```python
def get_git_metadata() -> tuple[str, str]:
    """
    Extract current git branch name and commit SHA.

    Returns:
        (branch_name, commit_sha) tuple
        - branch_name: Current branch (or "Unknown Branch" if unavailable)
        - commit_sha: Full commit SHA (or "Unknown SHA" if unavailable)

    Notes:
        - Never raises exceptions (always returns placeholders on error)
        - Timeout after 2 seconds (prevents hanging on slow git operations)
        - Uses `git` CLI (no external dependencies)
    """
```

### Return Value Specification

| Field | Type | Format | Fallback |
|-------|------|--------|----------|
| branch_name | str | Branch name (e.g., "main", "feature/add-comments") | "Unknown Branch" |
| commit_sha | str | Full 40-char hex SHA (e.g., "a1b2c3d4...") | "Unknown SHA" |

**Constraints**:
- `branch_name`: 1-255 chars, alphanumeric + `-/_` allowed
- `commit_sha`: 40 hex chars (lowercase) in normal case, "Unknown SHA" string in fallback

---

## Git Commands Used

### Branch Name Extraction

```bash
git rev-parse --abbrev-ref HEAD
```

**Behavior**:
- Normal branch: Returns branch name (e.g., "main")
- Detached HEAD: Returns "HEAD"
- Not a git repo: Exits with error (handled → fallback)

### Commit SHA Extraction

```bash
git rev-parse HEAD
```

**Behavior**:
- Normal state: Returns full 40-char SHA
- Initial commit (no HEAD): Exits with error (handled → fallback)
- Not a git repo: Exits with error (handled → fallback)

---

## Contract Test Scenarios

### 1. Normal Git Repository

**Setup**:
- Valid git repo with commits
- Current branch: "main"
- HEAD at commit "a1b2c3d4e5f67890..." (full SHA)

**Expected**:
```python
branch_name, commit_sha = get_git_metadata()
assert branch_name == "main"
assert len(commit_sha) == 40
assert all(c in "0123456789abcdef" for c in commit_sha)
```

### 2. Feature Branch

**Setup**:
- Branch name: "004-end-to-end"

**Expected**:
```python
branch_name, _ = get_git_metadata()
assert branch_name == "004-end-to-end"
```

### 3. Detached HEAD State

**Setup**:
- `git checkout <commit-sha>` (detached HEAD)

**Expected**:
```python
branch_name, commit_sha = get_git_metadata()
assert branch_name == "HEAD"  # git rev-parse --abbrev-ref HEAD returns "HEAD"
assert len(commit_sha) == 40  # SHA still available
```

**Note**: Spec allows "HEAD" as valid branch name (not an error state)

### 4. Not in Git Repository

**Setup**:
- Current directory is not a git repo (no `.git/` directory)

**Expected**:
```python
branch_name, commit_sha = get_git_metadata()
assert branch_name == "Unknown Branch"
assert commit_sha == "Unknown SHA"
```

### 5. Git Command Not Found

**Setup**:
- `git` executable not in PATH (simulated via mock)

**Expected**:
```python
# Same as scenario 4: graceful fallback
branch_name, commit_sha = get_git_metadata()
assert branch_name == "Unknown Branch"
assert commit_sha == "Unknown SHA"
```

### 6. Git Command Timeout

**Setup**:
- Mock `git` command to hang (simulate slow network filesystem)
- Timeout set to 2 seconds

**Expected**:
```python
# Should timeout and return fallback (not hang indefinitely)
branch_name, commit_sha = get_git_metadata()
assert branch_name == "Unknown Branch"
assert commit_sha == "Unknown SHA"
```

### 7. Git Worktree

**Setup**:
- Repository using `git worktree` (separate working directory)

**Expected**:
```python
# Should work normally (git commands work in worktrees)
branch_name, commit_sha = get_git_metadata()
assert branch_name != "Unknown Branch"  # Real branch name
assert len(commit_sha) == 40  # Real SHA
```

### 8. Git Submodule

**Setup**:
- Current directory is inside a git submodule

**Expected**:
```python
# Should work normally (submodules are valid git repos)
branch_name, commit_sha = get_git_metadata()
assert branch_name != "Unknown Branch"
assert len(commit_sha) == 40
```

---

## Error Handling Matrix

| Error Condition | Git Command Result | Function Behavior | Return Value |
|-----------------|-------------------|-------------------|--------------|
| Not a git repo | `CalledProcessError` | Catch exception | `("Unknown Branch", "Unknown SHA")` |
| Git not installed | `FileNotFoundError` | Catch exception | `("Unknown Branch", "Unknown SHA")` |
| Git timeout | `TimeoutExpired` | Catch exception | `("Unknown Branch", "Unknown SHA")` |
| Permission denied | `CalledProcessError` | Catch exception | `("Unknown Branch", "Unknown SHA")` |
| Detached HEAD | Returns "HEAD" | Normal operation | `("HEAD", <sha>)` |
| Empty repo (no commits) | `CalledProcessError` | Catch exception | `("Unknown Branch", "Unknown SHA")` |

**Principle**: Never crash, always return valid tuple with placeholders on any error

---

## Performance Requirements

| Metric | Target | Rationale |
|--------|--------|-----------|
| Normal case execution | <100ms | Two subprocess calls, minimal overhead |
| Timeout limit | 2 seconds | Prevents hanging on network FS or stalled git |
| Memory usage | <1MB | Subprocess overhead only, no caching needed |

**Implementation Note**: No caching needed (called once on quit, not in hot path)

---

## Contract Test Implementation

### Test File: `tests/contract/test_git_metadata.py`

**Test Structure**:
```python
import subprocess
from unittest.mock import patch
from racgoat.services.git_metadata import get_git_metadata

def test_normal_git_repo():
    """Raccoon sniffs out branch and commit from healthy git pile"""
    # Arrange: In actual git repo (tests run in RacGoat repo)
    # Act: Call function
    # Assert: Valid branch name and 40-char SHA

def test_detached_head():
    """Goat perches on detached HEAD, unbothered"""
    # Arrange: Checkout specific commit (setup in fixture)
    # Act: Call function
    # Assert: branch_name == "HEAD", SHA valid

def test_not_a_git_repo(tmp_path, monkeypatch):
    """Raccoon explores non-git territory, finds placeholders"""
    # Arrange: Change to temp dir (not a repo)
    # Act: Call function
    # Assert: Fallback values

def test_git_command_not_found():
    """Goat climbs mountain without git tools, survives"""
    # Arrange: Mock subprocess to raise FileNotFoundError
    # Act: Call function
    # Assert: Fallback values

def test_git_timeout():
    """Raccoon waits 2 seconds, then moves on"""
    # Arrange: Mock subprocess to raise TimeoutExpired
    # Act: Call function
    # Assert: Fallback values, completes in <3 seconds

def test_branch_name_with_slashes():
    """Raccoon handles fancy branch names like feature/my-thing"""
    # Arrange: Create branch "feature/test-branch"
    # Act: Call function
    # Assert: Full branch name preserved

def test_git_worktree():
    """Goat navigates worktree without confusion"""
    # Arrange: Create worktree (if test setup allows)
    # Act: Call function
    # Assert: Valid metadata from worktree
```

**Fixtures**:
- `git_repo_fixture`: Temporary git repo with commits
- `non_git_dir_fixture`: Temporary directory (not a repo)
- `detached_head_fixture`: Repo in detached HEAD state

---

## Implementation Guidance

### Subprocess Configuration

```python
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True,    # Capture stdout/stderr
    text=True,              # Decode as UTF-8
    check=True,             # Raise CalledProcessError on non-zero exit
    timeout=2               # Abort after 2 seconds
)
branch_name = result.stdout.strip()
```

**Key Parameters**:
- `capture_output=True`: Get stdout/stderr (not printed to terminal)
- `text=True`: Decode bytes to str (UTF-8)
- `check=True`: Exception on error (caught in outer try/except)
- `timeout=2`: Prevent hanging (per performance requirement)

### Error Handling Pattern

```python
try:
    branch = subprocess.run(...).stdout.strip()
    sha = subprocess.run(...).stdout.strip()
    return (branch, sha)
except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
    return ("Unknown Branch", "Unknown SHA")
```

---

## Integration Points

### Called By
- `racgoat/services/markdown_writer.py` → `serialize_review_session()`
- Invoked once during `RacGoatApp.action_quit()` flow

### Dependencies
- System `git` executable (no Python library dependencies)
- Current working directory (should be repository root)

---

## Versioning

**Contract Version**: 1.0.0

**Breaking Changes** (increment major):
- Change return type (e.g., return dict instead of tuple)
- Change placeholder values (apps may hardcode checks)

**Non-Breaking Changes** (increment minor):
- Add optional parameters (e.g., timeout override)
- Improve error messages (if logged)

---

## References

- Feature Spec: `specs/004-end-to-end/spec.md` (FR-005, FR-006)
- Research Doc: `specs/004-end-to-end/research.md` (Git Metadata Extraction section)
- Git CLI Docs: https://git-scm.com/docs/git-rev-parse

---

**Status**: Contract Defined ✅
**Next**: Implement contract tests (must fail before implementation)
