---
description: "Task list for including diff segments in review output"
---

# Tasks: Include Diff Segments in Review Output

**Input**: Design documents from `/specs/007-currently-the-review/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: This feature follows TDD approach - contract tests are written FIRST to validate functional requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project structure**: `racgoat/` for source, `tests/` at repository root
- Follows existing RacGoat architecture from Milestones 1-7

---

## Phase 1: Setup (Test Infrastructure)

**Purpose**: Prepare test files and fixtures for TDD workflow

- [X] T001 [P] Create contract test file `tests/contract/test_diff_segments.py` with base fixtures (sample_diff_file, sample_review_session)
- [X] T002 [P] Create performance test file `tests/integration/test_performance/test_diff_segment_performance.py` with setup
- [X] T003 Verify existing test suite baseline (run `uv run pytest tests/` - expect 98 tests passing)

**Checkpoint**: Test infrastructure ready for TDD workflow - COMPLETE

---

## Phase 2: Foundational (Core Function Implementation)

**Purpose**: Implement core diff segment extraction functions that all user stories depend on

**⚠️ CRITICAL**: These functions must be implemented before any user story can be completed

### Tests (Written FIRST - Red Phase)

- [X] T004 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_line_comment()` in `tests/unit/test_markdown_writer.py`
- [X] T005 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_range_comment()` in `tests/unit/test_markdown_writer.py`
- [X] T006 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_file_comment_returns_none()` in `tests/unit/test_markdown_writer.py`
- [X] T007 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_boundary_start()` in `tests/unit/test_markdown_writer.py`
- [X] T008 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_boundary_end()` in `tests/unit/test_markdown_writer.py`
- [X] T009 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_malformed_hunk()` in `tests/unit/test_markdown_writer.py`
- [X] T010 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_target_not_found()` in `tests/unit/test_markdown_writer.py`
- [X] T011 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_removed_lines_included()` in `tests/unit/test_markdown_writer.py`
- [X] T012 [P] [FOUNDATION] Write unit test `test_extract_diff_segment_context_zero()` in `tests/unit/test_markdown_writer.py`
- [X] T013 [P] [FOUNDATION] Write unit test `test_format_file_stats_normal_file()` in `tests/unit/test_markdown_writer.py`
- [X] T014 [P] [FOUNDATION] Write unit test `test_format_file_stats_new_file()` in `tests/unit/test_markdown_writer.py`
- [X] T015 [P] [FOUNDATION] Write unit test `test_format_file_stats_empty_file()` in `tests/unit/test_markdown_writer.py`

### Core Implementation (Green Phase)

- [X] T016 [FOUNDATION] Replace `extract_code_context()` with `extract_diff_segment()` in `racgoat/services/markdown_writer.py` (signature: see data-model.md:L137-144; implement line number mapping, context window, diff marker formatting per research.md algorithm)
- [X] T017 [P] [FOUNDATION] Implement `format_file_stats()` function in `racgoat/services/markdown_writer.py` (format: "N hunks, +X -Y lines")

### Validation

- [X] T018 Run unit tests - verify all 12 unit tests pass (Green phase complete)

**Checkpoint**: Foundation ready - user story implementation can now begin - COMPLETE

---

## Phase 3: User Story 1 - View Actual Changes in Review (Priority: P1) 🎯 MVP

**Goal**: Enable reviewers and AI agents to see actual diff segments (with +/- markers) in review.md for line comments

**Independent Test**: Create a line comment on a modified line, save review, verify output includes diff segment with +/- markers showing before/after changes

### Contract Tests for User Story 1 (Written FIRST - Red Phase)

- [X] T019 [P] [US1] Write contract test `test_diff_segment_included_for_line_comment()` in `tests/contract/test_diff_segments.py` (FR-001)
- [X] T020 [P] [US1] Write contract test `test_before_after_states_shown()` in `tests/contract/test_diff_segments.py` (FR-002)
- [X] T021 [P] [US1] Write contract test `test_context_lines_included()` in `tests/contract/test_diff_segments.py` (FR-003)
- [X] T022 [P] [US1] Write contract test `test_line_comment_has_two_context_lines()` in `tests/contract/test_diff_segments.py` (FR-004)
- [X] T023 [P] [US1] Write contract test `test_fenced_code_block_with_diff_syntax()` in `tests/contract/test_diff_segments.py` (FR-009)
- [X] T024 [P] [US1] Write contract test `test_unified_diff_format()` in `tests/contract/test_diff_segments.py` (FR-011)
- [X] T025 [P] [US1] Write contract test `test_backward_compatibility_no_diff_summary()` in `tests/contract/test_diff_segments.py` (FR-010)

### Implementation for User Story 1

- [X] T026 [US1] Update `serialize_review_session()` in `racgoat/services/markdown_writer.py` to call `extract_diff_segment()` for LineComment (change fenced block from ` ``` ` to ` ```diff `)
- [X] T027 [US1] Run contract tests for US1 - verify all 7 tests pass (Green phase)

### Integration Tests for User Story 1

- [X] T028 [US1] Write integration test `test_end_to_end_line_comment_with_diff_segment()` in `tests/integration/test_markdown_output.py` (full TUI workflow)
- [X] T029 [US1] Run integration test - verify passes

**Checkpoint**: User Story 1 complete - line comments now show diff segments with +/- markers

---

## Phase 4: User Story 2 - Range Comments with Full Diff Context (Priority: P2)

**Goal**: Show full diff segment (all changes within range) for range comments, capturing complete modification context

**Independent Test**: Create a range comment spanning 5 lines with mixed additions/deletions, verify output shows all diff lines with proper markers

### Contract Tests for User Story 2 (Written FIRST - Red Phase)

- [X] T030 [P] [US2] Write contract test `test_range_comment_includes_full_range_plus_context()` in `tests/contract/test_diff_segments.py` (FR-005)
- [X] T031 [P] [US2] Write contract test `test_boundary_respect()` in `tests/contract/test_diff_segments.py` (FR-007)

### Implementation for User Story 2

- [X] T032 [US2] Update `serialize_review_session()` in `racgoat/services/markdown_writer.py` to call `extract_diff_segment()` for RangeComment (change fenced block to ` ```diff `)
- [X] T033 [US2] Run contract tests for US2 - verify both tests pass

### Integration Tests for User Story 2

- [X] T034 [US2] Write integration test `test_end_to_end_range_comment_with_diff_segment()` in `tests/integration/test_markdown_output.py`
- [X] T035 [US2] Run integration test - verify passes

**Checkpoint**: User Stories 1 AND 2 complete - both line and range comments show diff segments

---

## Phase 5: User Story 3 - File-level Comments with Statistical Summary (Priority: P3)

**Goal**: Display statistical summary (hunk count and line changes) for file-level comments instead of detailed diff context

**Independent Test**: Add a file-level comment, verify output includes "N hunks, +X -Y lines" statistical summary

### Contract Tests for User Story 3 (Written FIRST - Red Phase)

- [X] T036 [P] [US3] Write contract test `test_file_comment_shows_statistical_summary()` in `tests/contract/test_diff_segments.py` (FR-006)

### Implementation for User Story 3

- [X] T037 [US3] Update `serialize_review_session()` in `racgoat/services/markdown_writer.py` to handle FileComment with `format_file_stats()` (add "**File changes**: {stats}" section)
- [X] T038 [US3] Run contract test for US3 - verify test passes

### Integration Tests for User Story 3

- [X] T039 [US3] Write integration test `test_end_to_end_file_comment_with_stats()` in `tests/integration/test_markdown_output.py`
- [X] T040 [US3] Run integration test - verify passes

**Checkpoint**: All user stories complete - line/range/file comments all have appropriate diff context

---

## Phase 6: Edge Cases & Hardening (Priority: P4)

**Purpose**: Handle edge cases and validate robustness

### Contract Tests for Edge Cases

- [X] T041 [P] Write contract test `test_malformed_hunk_graceful_handling()` in `tests/contract/test_diff_segments.py` (FR-008: Returns None, no exception raised - see data-model.md:L157)
- [X] T042 [P] Write contract test `test_edge_cases()` (removed-only, added-only, boundary) in `tests/contract/test_diff_segments.py` (FR-012)
- [X] T043 [P] Write contract test `test_no_truncation_for_large_hunks()` in `tests/contract/test_diff_segments.py` (FR-013)

### Validation

- [X] T044 Run all contract tests - verify all 13 tests pass (FR-001 to FR-013 validated)

**Checkpoint**: Edge cases handled - feature is hardened

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance validation, regression checks, and final validation

### Performance Validation

- [X] T045 Implement performance test `test_diff_segment_extraction_performance()` in `tests/integration/test_performance/test_diff_segment_performance.py` (validate <100ms for 100 comments - SC-004)
- [X] T046 Run performance test - verify passes (<100ms target met)

### Integration Tests (Multiple Comments)

- [X] T047 Write integration test `test_multiple_comments_same_file()` in `tests/integration/test_markdown_output.py` (3 comments with correct segments)
- [X] T048 Write integration test `test_large_hunk_no_truncation()` in `tests/integration/test_markdown_output.py` (100+ line hunk)
- [X] T049 Run integration tests - verify all 5 integration tests pass

### Regression Validation

- [X] T050 Run full test suite `uv run pytest tests/ -v` - verify all 128+ tests pass (98 existing + 30 new, SC-005)
- [X] T051 Fix any test failures related to output format changes (update test expectations if needed)

### Manual Validation

- [X] T052 Generate sample review with `git diff HEAD~1 | uv run python -m racgoat -o review.md` and verify output quality (SC-007)
- [X] T053 Compare before/after review.md outputs - confirm diff segments provide clearer context than line numbers

**Checkpoint**: Feature complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if multiple developers)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Edge Cases (Phase 6)**: Depends on all user stories complete
- **Polish (Phase 7)**: Depends on all phases complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (both modify same function but different branches)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (separate code path in serialize function)

### Within Each User Story

- Contract tests MUST be written and FAIL before implementation (TDD red phase)
- Core implementation before running tests (green phase)
- Integration tests after contract tests pass
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: All 3 tasks can run in parallel (different files)
- Phase 2 Tests (T004-T015): All 12 unit tests can be written in parallel (same file, but independent test functions)
- Phase 3 Contract Tests (T019-T025): All 7 tests can be written in parallel
- Phase 6 Contract Tests (T041-T043): All 3 tests can be written in parallel
- **User Stories**: Once Foundational phase completes, all three user stories (Phases 3, 4, 5) can be worked on in parallel by different developers

---

## Parallel Example: Foundational Phase Unit Tests

```bash
# Write all 12 unit tests in parallel (different developers or concurrent edits):
Task: "test_extract_diff_segment_line_comment() in tests/unit/test_markdown_writer.py"
Task: "test_extract_diff_segment_range_comment() in tests/unit/test_markdown_writer.py"
Task: "test_extract_diff_segment_file_comment_returns_none() in tests/unit/test_markdown_writer.py"
# ... (9 more tests)
```

## Parallel Example: User Stories (If Team Has Multiple Developers)

```bash
# After Phase 2 completes, launch user stories in parallel:
Developer A: Phase 3 (User Story 1) - Line comments
Developer B: Phase 4 (User Story 2) - Range comments
Developer C: Phase 5 (User Story 3) - File comments
# Each developer works independently on separate branches of serialize_review_session()
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T018) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T019-T029)
4. **STOP and VALIDATE**: Test line comments independently with sample diff
5. Deploy/demo MVP with just line comment support

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Core functions ready (T001-T018)
2. Add User Story 1 → Test independently → Deploy/Demo MVP (T019-T029)
3. Add User Story 2 → Test independently → Deploy/Demo (T030-T035)
4. Add User Story 3 → Test independently → Deploy/Demo (T036-T040)
5. Add Edge Cases → Harden (T041-T044)
6. Polish & Validate → Final release (T045-T053)

### Parallel Team Strategy (If Multiple Developers Available)

With 3 developers after Foundational phase completes:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (line comments) - T019-T029
   - Developer B: User Story 2 (range comments) - T030-T035
   - Developer C: User Story 3 (file comments) - T036-T040
3. Developers merge in priority order (US1 first, then US2, then US3)
4. Team completes Edge Cases + Polish together (T041-T053)

---

## Notes

- [P] tasks = different files or independent test functions, no dependencies
- [Story] label maps task to specific user story (US1, US2, US3) for traceability
- [FOUNDATION] label indicates blocking prerequisite for all user stories
- TDD workflow: Write tests FIRST (red) → Implement (green) → Verify (green stays green)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (confirms test is valid)
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Key files modified: `racgoat/services/markdown_writer.py` (primary target)
- Key files created: `tests/contract/test_diff_segments.py` (13 tests), unit tests (12 tests), integration tests (5 tests), performance test (1 test)
- Total new tests: 31 tests (exceeds 10-test requirement from SC-006)
- Performance target: <100ms for 100 comments (SC-004)
- Success criteria: All 13 functional requirements (FR-001 to FR-013) validated via contract tests

---

## Test Count Summary

- **Contract tests**: 13 (one per FR-001 to FR-013)
- **Unit tests**: 12 (foundational function behavior)
- **Integration tests**: 5 (end-to-end workflows)
- **Performance tests**: 1 (SC-004 validation)
- **Total new tests**: 31
- **Existing tests**: 98 (must continue passing - SC-005)
- **Final test count**: 129 tests

---

## Success Criteria Validation

- **SC-001**: Diff segments in 100% of cases → Validated by FR-001 to FR-005 tests
- **SC-002**: Edge case handling → Validated by FR-007, FR-008, FR-012 tests
- **SC-003**: AI agents can parse → Validated by FR-011 (standard unified diff format)
- **SC-004**: Performance <100ms → Validated by T045-T046 performance test
- **SC-005**: Existing tests pass → Validated by T050-T051 regression check
- **SC-006**: Minimum 10 new tests → 31 tests added (exceeds requirement)
- **SC-007**: Improved clarity → Validated by T052-T053 manual review
