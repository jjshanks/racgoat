# Research: CLI Git Diff Processor

**Feature**: 001-goal-create-a
**Date**: 2025-09-30
**Status**: Complete

## Overview
This document captures technical research and decisions for implementing a CLI tool that parses git diff from stdin and generates file summaries.

## Research Areas

### 1. Git Diff Format Parsing

**Decision**: Use standard library regex + line-by-line parsing
**Rationale**:
- Unified diff format is well-documented and stable
- Standard library avoids external dependencies (aligns with constitution principle of simplicity)
- Regex patterns sufficient for extracting file paths and line counts from hunk headers
- No need for heavyweight parsing libraries (GitPython, etc.) for read-only diff analysis

**Alternatives Considered**:
- GitPython: Rejected (heavy dependency, unnecessary for stdin-based parsing)
- difflib: Rejected (designed for generating diffs, not parsing existing ones)
- Dedicated diff parser libraries: Rejected (adds complexity, not needed for simple line counting)

**Implementation Pattern**:
```
Read stdin line-by-line:
  - Detect file headers: "diff --git a/... b/..." or "+++ b/..."
  - Detect binary marker: "Binary files ... differ"
  - Parse hunk headers: "@@ -X,Y +A,B @@" to extract line counts
  - Accumulate +/- counts per file
```

**References**:
- Unified diff format: https://www.gnu.org/software/diffutils/manual/html_node/Unified-Format.html
- Python re module: https://docs.python.org/3/library/re.html

---

### 2. Filtered File Detection (Binary and Generated)

**Decision**: Multi-strategy filtering approach
**Rationale**:
- Binary files detected via "Binary files ... differ" marker in diff
- Generated files filtered by extension patterns (FR-006 in spec)
- Path-based filtering for dist/build directories
- "Filtered files" is the umbrella term encompassing both binary and generated files

**Alternatives Considered**:
- Content inspection: Rejected (stdin doesn't provide full file content, only diff)
- Mimetype detection: Rejected (requires file system access, not available from stdin)
- Hardcoded list: Accepted for generated patterns (explicit in spec clarifications)

**Filter Patterns** (from spec clarifications):
- Extensions: `.lock`, `.min.js`, `.min.css`, `.map`, `.bundle.js`
- Specific files: `package-lock.json`, `yarn.lock`, `poetry.lock`
- Glob patterns: `*.generated.*`
- Directory paths: `dist/`, `build/`

**Implementation**:
```python
def is_filtered(file_path: str) -> bool:
    # Check extension patterns
    # Check directory prefixes
    # Return True if should be excluded
```

---

### 3. CLI Argument Parsing

**Decision**: Use argparse (standard library)
**Rationale**:
- Standard library, no dependencies
- Provides automatic help generation (required per FR-007a)
- Handles error messages + usage output
- Type validation for arguments

**Alternatives Considered**:
- Click: Rejected (external dependency, overkill for single `-o` flag)
- Manual sys.argv parsing: Rejected (doesn't provide help/error handling per FR-007a)
- Typer: Rejected (external dependency)

**Argument Specification**:
```python
parser = argparse.ArgumentParser(description="Parse git diff and generate summary")
parser.add_argument('-o', '--output',
                    default='review.md',
                    help='Output file path (default: review.md)')
```

---

### 4. Output Format

**Decision**: Plain text, one line per file, `path/to/file: +X -Y` format
**Rationale**:
- Explicit in FR-010 of spec
- Simple, parseable, human-readable
- Aligns with default filename `review.md` (Markdown-compatible)

**Alternatives Considered**:
- JSON: Rejected (not specified, harder to read for quick review)
- CSV: Rejected (overkill for simple summary)
- Markdown table: Deferred to future milestone (when full review features added)

**Example Output**:
```
src/main.py: +15 -3
tests/test_parser.py: +42 -0
racgoat/utils.py: +8 -12
```

---

### 5. Error Handling & Exit Codes

**Decision**: Exit 0 for success (including empty diff), exit 1 for all failures
**Rationale**:
- Explicit in FR-012 and clarifications
- Empty diff = successful processing (no output file created)
- Invalid args, malformed diff, write errors = exit 1

**Error Scenarios**:
1. **Empty diff**: Log message, skip file creation, exit 0
2. **Invalid CLI args**: Print error + usage to stderr, exit 1
3. **Malformed diff**: Print error to stderr, exit 1
4. **Output file write failure**: Print error to stderr, exit 1
5. **All filtered files**: Treated as empty diff, exit 0

**Implementation Pattern**:
```python
try:
    # Parse args, read stdin, process diff
    if no_changes:
        sys.exit(0)  # Success, no output
    write_output(...)
    sys.exit(0)
except InvalidDiffError:
    print(error, file=sys.stderr)
    sys.exit(1)
```

---

### 6. Testing Strategy

**Decision**: TDD with pytest, organized by test type (unit/integration/contract)
**Rationale**:
- Constitution Principle III: TDD is mandatory
- pytest already configured in pyproject.toml
- Test organization aligns with Phase 1 design (contracts first)

**Test Layers**:
1. **Contract tests**: Validate output format matches `path: +X -Y` pattern
2. **Unit tests**:
   - `test_diff_parser.py`: Parsing logic, line counting
   - `test_file_filter.py`: Binary/generated file detection
3. **Integration tests**: End-to-end CLI workflow (stdin → output file)

**Test Data Strategy**:
- Fixtures with sample diffs (empty, single file, multi-file, binary, filtered)
- Inline heredoc strings for small diffs
- Test files for large diff scenarios (if needed for performance validation)

---

## Dependencies Summary

**Production Dependencies**: None (standard library only)
- `argparse`: CLI argument parsing
- `sys`: stdin/stdout/exit codes
- `re`: Regex for diff parsing
- `pathlib`: Path manipulation (optional, can use os.path)

**Development Dependencies**:
- `pytest>=8.4.2` (already configured)

**Rationale**: Minimal dependencies align with constitution principles and reduce maintenance burden. Standard library provides all necessary functionality for this milestone.

---

## Performance Considerations

**Scale Target**: 100 files, 10k diff lines (per PRD)

**Optimization Strategy**:
- Line-by-line streaming (no full diff buffering in memory)
- Early filtering (detect binary/generated files during parse, skip counting)
- Single-pass processing (accumulate counts while parsing)

**Expected Performance**:
- Memory: O(n) where n = number of files (store file paths + counts)
- Time: O(m) where m = number of diff lines (single pass)
- For 10k lines: expect <100ms processing time

**No optimization needed** for this milestone scale. Future milestones (TUI with 100 files) may require viewport rendering, but CLI output is batch-only.

---

## Open Questions

None. All clarifications resolved in spec.md Session 2025-09-30.

---

## References

- Feature Spec: `/home/jjshanks/workspace/racgoat/specs/001-goal-create-a/spec.md`
- RacGoat Constitution: `/home/jjshanks/workspace/racgoat/.specify/memory/constitution.md`
- PRD Milestone 1: `/home/jjshanks/workspace/racgoat/docs/prd.md` (implied)
- Python argparse docs: https://docs.python.org/3/library/argparse.html
- Unified diff format: https://www.gnu.org/software/diffutils/manual/html_node/Unified-Format.html
