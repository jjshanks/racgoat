# Performance Contracts: Benchmarks & Viewport Rendering

## Contract: Initial Load Time

**Interface**: `RacGoatApp.run(diff_source: IO) -> None`

### Scenario 1: Small Diff (10 files, 100 lines)
**Given**: Diff with 10 files, 100 total lines

**When**: Application launched with `uv run python -m racgoat < small.diff`

**Then**:
- Time from launch → first frame rendered: **< 500ms**
- Files list populated with 10 items
- First file auto-selected and visible in DiffPane
- No blocking operations

**Test Implementation**:
```python
@pytest.mark.benchmark
async def test_initial_load_small_diff(benchmark):
    diff = load_fixture("small.diff")  # 10 files, 100 lines

    def load_app():
        app = RacGoatApp()
        app.load_diff(diff)
        return app

    result = benchmark(load_app)
    assert benchmark.stats.mean < 0.5  # 500ms
```

### Scenario 2: Medium Diff (50 files, 1000 lines)
**Given**: Diff with 50 files, 1000 total lines

**Then**:
- Load time: **< 1s**
- Lazy loading: Only selected file content rendered
- Other 49 files remain as LazyFileContent (not materialized)

### Scenario 3: Large Diff (100 files, 10k lines)
**Given**: Diff with 100 files, 10,000 total lines (max supported)

**Then**:
- Load time: **< 2s** (FR-001)
- Parse time: < 1s
- Render first file: < 1s
- Memory footprint: Only 1 file's Rich Text in memory
- Viewport: Only ~50 visible lines rendered initially

**Test Assertion**:
```python
async def test_large_diff_load_performance():
    diff = generate_diff(files=100, total_lines=10000)
    start = time.perf_counter()

    app = RacGoatApp()
    async with app.run_test() as pilot:
        await pilot.pause()  # Wait for first render

    duration_ms = (time.perf_counter() - start) * 1000
    assert duration_ms < 2000, f"Load took {duration_ms}ms, expected < 2000ms"
```

---

## Contract: File Switching Latency

**Interface**: `FilesPane.on_file_selected(event: FileSelected) -> None`

### Scenario 1: Switch Between Small Files
**Given**: 2 files, 50 lines each, user navigates from File A → File B

**Then**:
- File selection → DiffPane update: **< 100ms**
- LazyFileContent for File B materialized on demand
- Old File A content released (GC eligible)

### Scenario 2: Switch to Large File (1000 lines)
**Given**: User selects file with 1000 lines

**Then**:
- Selection → viewport render: **< 200ms** (FR-004)
- Only visible lines rendered (viewport optimization)
- Scroll position reset to top

**Test Implementation**:
```python
@pytest.mark.benchmark
async def test_file_switch_latency(benchmark):
    app = create_app_with_diff(files=10, lines_per_file=100)

    async def switch_file():
        async with app.run_test() as pilot:
            await pilot.press("down")  # Select next file
            await pilot.pause()

    result = benchmark(switch_file)
    assert benchmark.stats.mean < 0.2  # 200ms
```

---

## Contract: Scroll Responsiveness

**Interface**: `DiffPane.on_scroll(event: ScrollEvent) -> None`

### Scenario 1: Viewport Rendering (1000 line file)
**Given**: File with 1000 lines, viewport height = 50 lines

**When**: User presses PageDown (scroll 50 lines)

**Then**:
- Scroll action → new viewport render: **< 100ms** (FR-003)
- Only lines 50-100 rendered (previous 0-50 discarded)
- No full-file re-render

**Viewport State Transition**:
```
BEFORE:  ViewportState(start=0, end=50, total=1000)
ACTION:  PageDown key press
AFTER:   ViewportState(start=50, end=100, total=1000)
RENDER:  Only lines[50:100] passed to render_line()
```

### Scenario 2: Rapid Scrolling
**Given**: User holds down arrow key (rapid scroll events)

**Then**:
- Each scroll event processed in **< 100ms**
- No event queue backlog
- Smooth visual experience (no lag)

**Test Assertion**:
```python
async def test_rapid_scroll_performance():
    app = create_app_with_large_file(lines=1000)

    async with app.run_test() as pilot:
        timings = []
        for _ in range(20):  # 20 rapid scrolls
            start = time.perf_counter()
            await pilot.press("down")
            await pilot.pause()
            timings.append((time.perf_counter() - start) * 1000)

        assert max(timings) < 100, f"Slowest scroll: {max(timings)}ms"
        assert sum(timings) / len(timings) < 50, "Average too slow"
```

### Scenario 3: Jump to End (Large File)
**Given**: 10k line file, user presses End key

**Then**:
- Jump → render: **< 200ms**
- Viewport jumps to last 50 lines (9950-10000)
- No intermediate renders

---

## Contract: Comment Addition Latency

**Interface**: `CommentStore.add_comment(comment: Comment) -> None`

### Scenario 1: Add Line Comment
**Given**: User at line 500, presses 'a', enters comment text

**Then**:
- Key press → modal open: **< 50ms** (TUI-First Experience principle)
- Comment submission → store update → visual marker: **< 200ms** (FR-004)
- DiffPane updates to show `*` marker next to line

### Scenario 2: Add Comment with 100 Existing Comments
**Given**: 100 comments already in store, user adds 101st

**Then**:
- Store insertion: **< 10ms** (in-memory dict operation)
- UI update: **< 200ms** (render marker in viewport)
- No performance degradation vs 1st comment

**Test Implementation**:
```python
@pytest.mark.benchmark
async def test_comment_addition_performance(benchmark):
    app = create_app_with_comments(existing=100)

    async def add_comment():
        async with app.run_test() as pilot:
            await pilot.press("a")  # Open comment modal
            await pilot.press(*"Test comment")
            await pilot.press("enter")
            await pilot.pause()

    result = benchmark(add_comment)
    assert benchmark.stats.mean < 0.2  # 200ms total
```

---

## Contract: Lazy Loading Behavior

**Interface**: `LazyFileContent.materialize() -> Text`

### Scenario 1: Unselected Files Not Materialized
**Given**: 100 files in diff, only File #1 selected

**Then**:
- Files #2-100: `is_materialized=False`, `rich_text=None`
- Memory usage: Only File #1's Rich Text allocated
- Estimated memory: ~1MB per file → 99MB saved

### Scenario 2: Materialization on Selection
**Given**: User switches from File #1 → File #2

**Then**:
- File #2 materialization: **< 100ms** (included in file switch latency)
- Rich Text built from DiffFile hunks
- Syntax highlighting applied
- Malformed hunks rendered with `[⚠ UNPARSEABLE]` prefix

**Test Assertion**:
```python
async def test_lazy_loading_memory_efficiency():
    app = create_app_with_diff(files=100)

    async with app.run_test() as pilot:
        lazy_files = app.lazy_files
        materialized_count = sum(1 for lf in lazy_files.values() if lf.is_materialized)

        assert materialized_count == 1, "Only selected file materialized"

        await pilot.press("down")  # Select next file
        await pilot.pause()

        materialized_count = sum(1 for lf in lazy_files.values() if lf.is_materialized)
        assert materialized_count == 2, "Previous + new file materialized"
```

### Scenario 3: Optional Memory Release (File Deselection)
**Given**: Implementation decision to release old file content on switch

**Then**:
- When File #1 deselected → `lazy_files["file1"].rich_text = None`
- `is_materialized` reset to False
- Next re-selection triggers re-materialization
- Trade-off: Lower memory vs re-render cost on revisit

---

## Performance Summary Table

| Operation | Threshold | Test Fixture | FR Reference |
|-----------|-----------|--------------|--------------|
| Initial Load (small) | < 500ms | 10 files, 100 lines | FR-001 |
| Initial Load (large) | < 2s | 100 files, 10k lines | FR-001 |
| File Switch | < 200ms | Any file pair | FR-004 |
| Scroll (viewport) | < 100ms | 1000 line file | FR-003 |
| Comment Add | < 200ms | Any comment | FR-004 |
| Materialization | < 100ms | Single file | FR-005 |

**All thresholds enforced via pytest-benchmark assertions in `tests/integration/test_performance/`**
