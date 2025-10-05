# Research: Performance Hardening & Final Polish

## Technical Decisions

### 1. Viewport Rendering Strategy

**Decision**: Textual's built-in `VerticalScroll` widget with content virtualization

**Rationale**:
- Textual 6.2.0+ provides `VerticalScroll` with efficient viewport management
- DiffPane (currently extends `Static`) will be refactored to use `VerticalScroll` container
- Only visible lines rendered via `render_line()` callback pattern
- Leverages Textual's internal virtual scrolling optimizations (tested at 100k+ lines in Textual docs)

**Alternatives Considered**:
- Custom scroll implementation → Rejected: reinvents tested Textual patterns, higher bug risk
- Third-party virtual scroll library → Rejected: adds dependency, conflicts with Textual event loop

**Implementation Pattern**:
```python
class DiffPane(VerticalScroll):
    def render_line(self, y: int) -> RenderableType:
        # Return only the line at viewport offset y
        # Malformed hunks rendered as Text("[UNPARSEABLE] " + raw_text, style="dim red")
```

### 2. Lazy Loading Architecture

**Decision**: File content materialization on selection event

**Rationale**:
- FilesPane already dispatches `FileSelected` message (Milestone 2)
- Parser outputs `DiffFile` with hunks list (parsing complete at load)
- "Lazy" means DiffPane constructs Rich Text only for selected file (not pre-rendering all files)
- Memory optimization: 100 files * 100 lines avg = 10k lines, but only ~50 lines visible at once

**Alternatives Considered**:
- Lazy parsing (defer hunk extraction) → Rejected: complicates error detection (need full parse for line count limit)
- Pre-render all files → Rejected: violates FR-005, causes 2s+ delays for 100-file diffs

**Implementation Pattern**:
- `on_file_selected()`: Clear DiffPane, build Text from selected DiffFile's hunks
- Viewport only renders visible subset of that Text

### 3. Malformed Hunk Detection

**Decision**: Try/catch blocks in parser with fallback to raw text storage

**Rationale**:
- Parser currently raises exceptions on malformed hunks (Milestone 1 behavior)
- FR-011 requires "continue functioning" → catch parse errors, store raw hunk text
- DiffHunk model extended with `is_malformed: bool` and `raw_text: Optional[str]`
- Visual indicator: prefix malformed hunks with `[⚠ UNPARSEABLE]` in dim red (raccoon warning symbol)

**Alternatives Considered**:
- Skip malformed hunks → Rejected: loses diff context, violates data integrity principle
- Fail entire file → Rejected: too aggressive, breaks FR-011 "continue functioning"

**Error Categories Detected**:
1. Invalid hunk header (regex: `@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@`)
2. Mismatched line counts (actual vs header-declared counts)
3. Missing content after header

### 4. Performance Benchmarking Infrastructure

**Decision**: pytest-benchmark integration with predefined diff fixtures

**Rationale**:
- pytest-benchmark provides statistical analysis (mean, stddev, min, max)
- Fixtures: small.diff (10 files/100 lines), medium.diff (50 files/1000 lines), large.diff (100 files/10k lines)
- Automated assertions: `assert benchmark.stats.mean < 2.0` (for 2s load requirement)
- Textual's `pilot()` test harness measures key press → render latency

**Alternatives Considered**:
- Manual timing with `time` module → Rejected: no statistical rigor, manual verification needed
- Separate perf test suite → Rejected: adds CI complexity, prefer pytest integration

**Benchmark Coverage** (FR-013):
- `test_initial_load_time()`: App launch → first render
- `test_file_switch_latency()`: FileSelected → DiffPane update
- `test_scroll_responsiveness()`: Key press → scroll render
- `test_comment_addition_latency()`: 'a' key → comment modal → store update

### 5. 10k Line Limit Enforcement

**Decision**: Pre-parse line count check with early exit error modal

**Rationale**:
- Count total lines during initial parse (single pass)
- If count > 10,000: raise `DiffTooLargeError` before building data structures
- RacGoatApp catches exception → display error modal → exit on dismiss
- Error message: "🦝 This diff is too large! RacGoat can handle up to 10,000 lines, but this diff has {count}. Consider reviewing in smaller chunks. 🐐"

**Alternatives Considered**:
- Progressive loading with warning → Rejected: clarification specified hard limit (option A in /clarify)
- Truncate to 10k lines → Rejected: loses context, violates data integrity

### 6. TUI Test Rewrite Strategy (FR-020)

**Decision**: Textual `pilot()` with snapshot assertions for binary file exclusion

**Rationale**:
- Old tests: assert app exits immediately (CLI behavior)
- New tests: assert `FilesPane.query(ListView).children` excludes .png/.jpg/.lock files
- Textual pilot allows programmatic TUI interaction without rendering
- Snapshot: "No reviewable files" message appears when all files binary

**Test Structure**:
```python
async def test_binary_files_excluded_from_list():
    diff = create_diff_with_only_binaries()
    app = RacGoatApp()
    async with app.run_test() as pilot:
        files_pane = app.query_one(FilesPane)
        assert len(files_pane.query(ListView).children) == 0
        assert "No reviewable files" in app.query_one(Footer).text
```

### 7. UI Consistency Audit Process

**Decision**: Grep-based text audit with checklist in tasks.md

**Rationale**:
- FR-015 to FR-019 require consistency across help text, keybindings, grammar
- Automated: `grep -r "Ctrl\|Control\|^" racgoat/` to find keybinding variations
- Manual review: status bar messages, error messages, help overlay
- Checklist items: raccoon/goat theme presence, grammar check, keybinding format standardization

**Alternatives Considered**:
- Linting tool for UI text → Rejected: no existing tool for Textual, over-engineering for v1

## Research Complete

All technical unknowns resolved. No NEEDS CLARIFICATION markers remain.

**Key Risks Identified**:
1. Textual VerticalScroll performance at 10k lines (mitigation: viewport rendering)
2. Malformed hunk edge cases not in test corpus (mitigation: real-world diff benchmarking per FR-012)
3. Pilot test flakiness with async TUI rendering (mitigation: use `pilot.pause()` for render completion)

**Dependencies Confirmed**:
- No new dependencies required (Textual 6.2.0+ sufficient)
- pytest-benchmark already in dev dependencies (verify with `uv tree`)

**Next Phase**: Design contracts and data model based on research decisions.
