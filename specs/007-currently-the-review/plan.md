# Implementation Plan: Include Diff Segments in Review Output

**Branch**: `007-currently-the-review` | **Date**: 2025-10-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-currently-the-review/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the Markdown review output to include actual diff segments (with +/- markers) instead of only post-change code context. This provides critical before/after context for reviewers and AI agents analyzing feedback. Line/range comments will show diff segments with ±2 context lines; file-level comments will show statistical summaries. Implementation requires modifying the `extract_code_context` and `serialize_review_session` functions in `markdown_writer.py`.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Textual 6.2.0+ (TUI framework)
**Storage**: In-memory comment storage, file-based Markdown output
**Testing**: pytest with contract/integration/unit test structure
**Target Platform**: Linux/macOS/Windows terminal environments
**Project Type**: Single TUI application (terminal-based)
**Performance Goals**: <100ms diff segment extraction per comment, <5s serialization for 100 comments
**Constraints**: Must maintain backward compatibility with existing Markdown output, no new external dependencies
**Scale/Scope**: Support up to 100 files with 10k total diff lines, handle hunks up to 100+ lines without truncation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution template is not yet populated for this project. Deriving principles from existing codebase patterns (CLAUDE.md, test structure, architectural decisions):

### Principle I: Test-First Development
- ✅ **PASS**: Feature spec includes comprehensive test scenarios (User Stories 1-3 with acceptance criteria)
- ✅ **PASS**: Success criteria explicitly requires "minimum 10 new tests" (SC-006)
- ✅ **PASS**: Contract/integration/unit test structure already established

### Principle II: Backward Compatibility
- ✅ **PASS**: FR-010 mandates backward compatibility when diff_summary is not provided
- ✅ **PASS**: Existing tests must continue passing (SC-005)
- ✅ **PASS**: No breaking changes to serialization API

### Principle III: Performance Standards
- ✅ **PASS**: Performance goals defined (<100ms extraction, <5s for 100 comments)
- ✅ **PASS**: SC-004 validates minimal performance impact
- ✅ **PASS**: Aligns with existing Milestone 6 performance benchmarks

### Principle IV: Minimal Dependencies
- ✅ **PASS**: No new external dependencies required (constraint in Technical Context)
- ✅ **PASS**: Uses existing DiffHunk/DiffFile models from parser
- ✅ **PASS**: Pure enhancement to existing markdown_writer.py

### Principle V: Edge Case Handling
- ✅ **PASS**: FR-008 requires graceful handling of malformed hunks
- ✅ **PASS**: FR-012 explicitly lists edge cases to handle
- ✅ **PASS**: Spec includes comprehensive edge case section

**Gate Status**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

---

**Post-Design Re-evaluation** (After Phase 1):

### Principle I: Test-First Development (Re-check)
- ✅ **PASS**: Contract tests fully specified (13 tests in test_requirements.md)
- ✅ **PASS**: Unit tests defined (12 tests for new functions)
- ✅ **PASS**: TDD workflow documented in quickstart.md (red-green-refactor)

### Principle II: Backward Compatibility (Re-check)
- ✅ **PASS**: Function contracts guarantee backward compatibility (FR-010)
- ✅ **PASS**: No breaking changes to data models
- ✅ **PASS**: Existing tests will continue to pass (verified in design)

### Principle III: Performance Standards (Re-check)
- ✅ **PASS**: Performance contract defined (<100ms for 100 comments)
- ✅ **PASS**: Algorithm complexity analyzed (O(n) per hunk, acceptable)
- ✅ **PASS**: Performance test specified in test_requirements.md

### Principle IV: Minimal Dependencies (Re-check)
- ✅ **PASS**: Zero new dependencies added
- ✅ **PASS**: Pure transformation layer modification
- ✅ **PASS**: Reuses existing parser models (DiffHunk, DiffFile)

### Principle V: Edge Case Handling (Re-check)
- ✅ **PASS**: All edge cases documented in data-model.md
- ✅ **PASS**: Malformed hunk handling specified (returns None gracefully)
- ✅ **PASS**: Boundary conditions tested (FR-007, FR-012)

**Final Gate Status**: ✅ ALL GATES PASSED POST-DESIGN - Ready for Implementation (Phase 2)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
racgoat/
├── models/
│   └── comments.py          # Comment models (ReviewSession, SerializableComment, etc.)
├── services/
│   └── markdown_writer.py   # 🎯 PRIMARY MODIFICATION TARGET
│       ├── extract_code_context()        # REPLACE: Change from post-change code to diff segments
│       ├── serialize_review_session()    # MODIFY: Add statistical summary for file comments
│       └── write_markdown_output()       # UNCHANGED: Atomic file write logic
├── parser/
│   └── models.py            # DiffHunk, DiffFile, DiffSummary (READ-ONLY)
└── constants.py             # DEFAULT_CONTEXT_LINES=2 (READ-ONLY)

tests/
├── contract/
│   └── test_diff_segments.py         # NEW: 10+ tests for diff segment accuracy
├── integration/
│   └── test_markdown_output.py       # EXTEND: Add diff segment integration tests
└── unit/
    └── test_markdown_writer.py       # EXTEND: Add extract_diff_segment unit tests
```

**Structure Decision**: Single project structure (Option 1). This is a pure enhancement to the existing `markdown_writer.py` service. No new files required in main source tree - only modifications to `extract_code_context()` function to extract diff segments instead of post-change code, and minor changes to `serialize_review_session()` for file-level statistical summaries. New tests will be added to existing test directories following the contract/integration/unit pattern established in Milestones 1-7.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations detected** - All gates passed. No complexity justifications required.
