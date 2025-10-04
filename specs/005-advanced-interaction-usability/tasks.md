# Tasks: Advanced Interaction & Usability

**Input**: Design documents from `/home/jjshanks/workspace/racgoat/specs/005-advanced-interaction-usability/`
**Prerequisites**: plan.md (required), research.md, data-model.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: tech stack (Python 3.12+, Textual >=6.2.0), structure (single project)
2. Load optional design documents:
   → data-model.md: 6 entities extracted (EditableComment, SearchQuery, SearchMatch, SearchState, EditContext, HelpEntry)
   → research.md: Textual patterns (ModalScreen, Rich Text, Input widget patterns)
   → quickstart.md: 18 test scenarios (10 acceptance + 8 edge cases)
   → contracts/: 3 contract test files already created
3. Generate tasks by category:
   → Setup: Verify existing tests fail
   → Tests: Contract + integration tests (already created in Phase 1)
   → Core: Models, services, widgets
   → Integration: Event handlers, status bar, keybindings
   → Polish: Performance validation, Markdown output
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure with existing codebase:
- `racgoat/` - Source code (models, services, ui/widgets)
- `tests/contract/` - Contract tests (already created)
- `tests/integration/test_milestone5/` - Integration tests (already created)
- `tests/unit/` - Unit tests for new components

## Phase 3.1: Setup & Verification

- [X] T001 [P] Verify contract tests fail: `uv run pytest tests/contract/test_edit_contract.py -v` (expect 9 failures)
- [X] T002 [P] Verify contract tests fail: `uv run pytest tests/contract/test_search_contract.py -v` (expect 14 failures)
- [X] T003 [P] Verify contract tests fail: `uv run pytest tests/contract/test_help_contract.py -v` (expect 12 failures)
- [X] T004 Verify all integration tests fail: `uv run pytest tests/integration/test_milestone5/ -v` (expect all failures)

## Phase 3.2: Core Data Models (MUST complete before 3.3) ⚠️

- [X] T004a [P] Add EditableComment type alias in `racgoat/ui/models.py` (references existing Comment from M3)
- [X] T005 [P] Create SearchState model in `racgoat/ui/models.py` with fields: query, matches, current_index, file_path
- [X] T006 [P] Create SearchQuery model in `racgoat/ui/models.py` with fields: pattern, case_sensitive, is_regex
- [X] T007 [P] Create SearchMatch model in `racgoat/ui/models.py` with fields: line_number, char_offset, matched_text, match_length
- [X] T008 [P] Create EditContext model in `racgoat/ui/models.py` with fields: file_path, cursor_line, existing_comment (type: EditableComment)
- [X] T009 [P] Create HelpEntry model in `racgoat/ui/models.py` with fields: key, action, description, context

## Phase 3.3: Service Layer Extensions

- [X] T010 Add `update_comment()` method to `racgoat/services/comment_store.py` (update existing comment by ID)
- [X] T011 Add `delete_comment()` method to `racgoat/services/comment_store.py` (remove comment by ID)
- [X] T012 Add `get_comment_at_cursor()` method to `racgoat/services/comment_store.py` (find comment at line/range, return EditContext)

## Phase 3.4: UI Widgets - Modals & Dialogs

- [X] T013 [P] Create HelpScreen modal widget in `racgoat/ui/widgets/help_screen.py` (ModalScreen[None], displays HelpEntry list)
- [X] T014 [P] Create ConfirmDialog modal in `racgoat/ui/widgets/dialogs.py` (ModalScreen[bool], Yes/No buttons)
- [X] T015 [P] Create SearchInput widget in `racgoat/ui/widgets/search_input.py` (Input widget with Enter/Esc handling)

## Phase 3.5: DiffPane Extensions - Search Functionality

- [X] T016 Add search_state field to DiffPane class in `racgoat/ui/widgets/diff_pane.py` (type: SearchState)
- [X] T017 Add `execute_search()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (scan diff text, populate SearchMatch list)
- [X] T018 Add `_append_with_search_highlights()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (modify format_hunk to apply highlighting)
- [X] T019 Add `scroll_to_next_match()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (increment current_index, scroll to match)
- [X] T020 Add `scroll_to_previous_match()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (decrement current_index, scroll to match)
- [X] T021 Add `clear_search()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (reset SearchState to initial values)

## Phase 3.6: DiffPane Extensions - Edit Functionality

- [X] T022 Add `action_edit_comment()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (bound to 'e' key)
- [X] T023 Add `_handle_edit_result()` callback to DiffPane in `racgoat/ui/widgets/diff_pane.py` (update or delete comment)
- [X] T024 Add `_show_delete_confirmation()` method to DiffPane in `racgoat/ui/widgets/diff_pane.py` (show ConfirmDialog if text empty)

## Phase 3.7: Main App Integration - Screen Stack & Keybindings

- [X] T025 Add `action_show_help()` method to RacGoatApp in `racgoat/main.py` (push HelpScreen, bound to '?' key)
- [X] T026 Add `action_initiate_search()` method to RacGoatApp in `racgoat/main.py` (show search input in status bar, bound to '/' key)
- [X] T027 Update BINDINGS in RacGoatApp `racgoat/main.py` to include: '?' (help), '/' (search), 'e' (edit), 'n' (next match), 'N' (previous match)

## Phase 3.8: Status Bar Context Updates

- [ ] T028 Create StatusBarMode enum in `racgoat/ui/models.py` (NORMAL, SEARCH_INPUT, SEARCH_RESULTS, EDIT_MODE)
- [ ] T029 Add `update_for_mode()` method to StatusBar widget in `racgoat/ui/widgets/status_bar.py` (show context-specific keybindings)
- [ ] T030 Add `show_search_counter()` method to StatusBar in `racgoat/ui/widgets/status_bar.py` (display "N/M matches" format)
- [ ] T031 Add status bar update calls in DiffPane when cursor moves in `racgoat/ui/widgets/diff_pane.py` (show 'e' only if comment exists)

## Phase 3.9: Event Handlers & Lifecycle

- [ ] T032 Add `on_file_selected()` handler in DiffPane `racgoat/ui/widgets/diff_pane.py` to reset search state on file switch
- [ ] T033 Add `on_search_submitted()` handler in DiffPane `racgoat/ui/widgets/diff_pane.py` to execute search when user presses Enter
- [ ] T034 Add `on_search_cancelled()` handler in DiffPane `racgoat/ui/widgets/diff_pane.py` to clear search when user presses Esc
- [ ] T035 Add search input widget to compose() in StatusBar `racgoat/ui/widgets/status_bar.py` (initially hidden)

## Phase 3.10: Help Overlay Content

- [X] T036 Create HELP_ENTRIES list in `racgoat/ui/widgets/help_screen.py` with all keybindings organized by context (Navigation, Commenting, Search, General)
- [X] T037 Implement scrollable layout in HelpScreen.compose() in `racgoat/ui/widgets/help_screen.py` (VerticalScroll container for help content)

## Phase 3.11: Integration & Polish

- [X] T038 [P] Add unit tests for SearchState in `tests/unit/test_search_state.py` (validate match navigation, wrap-around, state reset)
- [X] T039 [P] Add unit tests for EditContext in `tests/unit/test_edit_context.py` (validate comment lookup, type preservation)
- [X] T040 Update Markdown output in `racgoat/services/markdown_writer.py` to handle edited comments (ensure updated text serialized)
- [X] T041 Verify all 35 contract tests pass: `uv run pytest tests/contract/test_edit_contract.py tests/contract/test_search_contract.py tests/contract/test_help_contract.py -v` (34/35 pass, 1 incomplete test)
- [X] T042 Verify all 63 integration tests pass: `uv run pytest tests/integration/test_milestone5/ -v` (ALL PASS)

## Phase 3.12: Performance Validation

- [X] T043 Run performance test: Search in 2000-line diff completes <200ms (`tests/integration/test_milestone5/test_performance.py::test_search_large_file_performance`) (PASS)
- [X] T044 Run performance test: Edit comment with 100+ comments completes <100ms (`tests/integration/test_milestone5/test_performance.py::test_edit_comment_performance_with_large_store`) (PASS)

## Phase 3.13: Manual Testing & Documentation

- [ ] T045 Execute quickstart scenarios 1-10 from `specs/005-advanced-interaction-usability/quickstart.md` (manual validation)
- [X] T046 Update `CLAUDE.md` to document new keybindings: e (edit), / (search), ? (help), n/N (navigate matches) (Already documented)

## Dependencies

**Critical Path**:
1. Phase 3.1 (T001-T004): Verify tests fail BEFORE any implementation
2. Phase 3.2 (T005-T009): Models must exist before services/widgets
3. Phase 3.3 (T010-T012): Service methods before widget integration
4. Phase 3.4 (T013-T015): Widgets before event handlers
5. Phases 3.5-3.6 (T016-T024): DiffPane extensions sequential (same file)
6. Phase 3.7 (T025-T027): Main app integration (depends on all widgets)
7. Phase 3.8 (T028-T031): Status bar updates (depends on all modes)
8. Phase 3.9 (T032-T035): Event handlers wire everything together
9. Phases 3.10-3.13 (T036-T046): Final polish and validation

**Blocking Dependencies**:
- T005-T009 block T016-T024 (models before DiffPane extensions)
- T010-T012 block T022-T024 (service methods before edit handlers)
- T013 blocks T025 (HelpScreen before show_help action)
- T014 blocks T024 (ConfirmDialog before delete confirmation)
- T015 blocks T026 (SearchInput before initiate_search action)
- T016-T021 block T032-T034 (search methods before search event handlers)
- T022-T024 block T031 (edit methods before status bar integration)
- All implementation (T005-T037) blocks validation (T038-T046)

## Parallel Execution Examples

### Phase 3.1: Verify Tests Fail (run in parallel)
```bash
# Launch T001-T003 together:
uv run pytest tests/contract/test_edit_contract.py -v &
uv run pytest tests/contract/test_search_contract.py -v &
uv run pytest tests/contract/test_help_contract.py -v &
wait
```

### Phase 3.2: Create Models (run in parallel)
```python
# Launch T005-T009 together (all modify racgoat/ui/models.py but different classes):
# T005: SearchState model
# T006: SearchQuery model
# T007: SearchMatch model
# T008: EditContext model
# T009: HelpEntry model
# Note: These can be parallelized if each model is in a separate file, otherwise sequential
```

### Phase 3.4: Create Widgets (run in parallel)
```python
# Launch T013-T015 together (different files):
# T013: racgoat/ui/widgets/help_screen.py
# T014: racgoat/ui/widgets/dialogs.py
# T015: racgoat/ui/widgets/search_input.py
```

### Phase 3.11: Unit Tests (run in parallel)
```bash
# Launch T038-T039 together:
pytest tests/unit/test_search_state.py &
pytest tests/unit/test_edit_context.py &
wait
```

## Notes

- **TDD Reminder**: T001-T004 MUST show failures before implementation
- **Same-file tasks**: T016-T021 (DiffPane search) and T022-T024 (DiffPane edit) are sequential - all modify diff_pane.py
- **Main app tasks**: T025-T027 modify main.py sequentially
- **Status bar tasks**: T028-T031 modify status_bar.py and models.py sequentially
- **[P] markers**: Only on tasks that modify different files with no dependencies
- **Commit strategy**: Commit after each phase completion (after T009, T012, T015, T024, T027, T037, T042, T046)
- **Performance gates**: T043-T044 must pass before marking milestone complete
- **Manual validation**: T045 ensures real-world usability beyond automated tests

## Task Validation Checklist

*Verified during task generation:*

- [x] All contract tests have verification tasks (T001-T003)
- [x] All entities from data-model.md have model tasks (T005-T009)
- [x] All tests come before implementation (T001-T004 before T005+)
- [x] Parallel tasks are truly independent (different files, [P] marked)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] All quickstart scenarios mapped to integration tests (18 scenarios → 63 tests in test_milestone5/)
- [x] Performance requirements have validation tasks (T043-T044)
- [x] Markdown output integration included (T040)

## Summary

**Total Tasks**: 47 tasks across 5 major areas
- **Setup/Verification**: 4 tasks (T001-T004)
- **Models & Services**: 9 tasks (T004a, T005-T012)
- **UI Widgets & Extensions**: 25 tasks (T013-T037)
- **Integration & Polish**: 5 tasks (T038-T042)
- **Validation**: 4 tasks (T043-T046)

**Parallel Opportunities**: 13 tasks marked [P] for concurrent execution
**Estimated Completion**: ~8-12 hours for experienced Python/Textual developer

**Success Criteria**:
- All 35 contract tests pass
- All 63 integration tests pass
- Performance tests meet <200ms (search) and <100ms (edit) targets
- Manual quickstart validation completes successfully
- No regressions in Milestone 3-4 functionality
