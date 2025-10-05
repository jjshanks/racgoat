
# Implementation Plan: Performance Hardening & Final Polish

**Branch**: `006-performance-hardening-final` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/006-performance-hardening-final/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Performance Hardening & Final Polish milestone ensures RacGoat can handle production-scale diffs (100 files, 10,000 lines) with robust error handling, consistent UI/UX, and comprehensive test coverage. Key deliverables: viewport rendering + lazy loading for performance, malformed diff handling with visual indicators, 10k line hard limit enforcement, automated performance benchmarks, rewritten TUI-compatible binary filtering tests, and UI consistency polish across all help text and error messages.

## Technical Context
**Language/Version**: Python 3.12+
**Primary Dependencies**: Textual 6.2.0+ (TUI framework), Rich (syntax highlighting via Textual)
**Storage**: In-memory (comment store), file system (Markdown output)
**Testing**: pytest 8.4.2+, pytest-asyncio 1.2.0+ (for Textual widget testing)
**Target Platform**: Linux/macOS/WSL terminal environments (80x24 minimum)
**Project Type**: Single project (TUI application)
**Performance Goals**: <2s initial load (100 files/10k lines), <200ms UI interactions, <100ms scroll
**Constraints**: 10,000 line hard limit, viewport-only rendering, lazy file loading, <50ms input response (per constitution)
**Scale/Scope**: Up to 100 files per diff, up to 10,000 total lines, unlimited comments per review session

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fun Is a Feature (NON-NEGOTIABLE)
✅ **PASS** - Performance hardening maintains raccoon/goat theme in error messages (malformed hunks shown as "unparseable" with visual indicator fits the "goats climb rocky cliffs" metaphor). Test names will follow punny conventions. UI polish includes thematic consistency review (FR-019).

### II. TUI-First Experience
✅ **PASS** - All performance requirements (<50ms input response per constitution, <100ms scroll per spec) directly enhance TUI experience. Viewport rendering (FR-003) ensures terminal responsiveness. Keyboard-only navigation preserved across all error handling flows.

### III. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - FR-013 mandates automated performance tests. FR-020 requires rewriting binary filtering tests as TUI tests. All contract tests must exist before implementation. Integration tests map to acceptance scenarios 1-6.

### IV. Performance Within Constraints
✅ **PASS** - Core milestone objective. FR-001 to FR-005 enforce PRD limits (100 files, 10k lines). FR-002a adds hard limit enforcement. Lazy loading (FR-005) and viewport rendering (FR-003) are constitutional requirements.

### V. Data Integrity Over Convenience
✅ **PASS** - FR-009 ensures no comment data loss during parsing errors. Git metadata already captured (Milestone 4). Malformed hunk handling (FR-011) preserves raw text to maintain diff context accuracy.

### VI. Graceful Degradation
✅ **PASS** - Primary milestone focus. FR-006 to FR-011 handle malformed diffs, invalid hunks, I/O errors. FR-002a provides clear error for oversized diffs. Edge case testing (FR-014) validates Unicode, long lines, empty files.

**Initial Gate Result**: ✅ PASS - All constitutional principles aligned with milestone requirements.

---

**Post-Design Constitution Re-Check** (after Phase 1):

### I. Fun Is a Feature (NON-NEGOTIABLE)
✅ **PASS** - Malformed hunk error messages maintain theme (`[⚠ UNPARSEABLE]` visual indicator, raccoon/goat emoji bookends on all errors). Contract tests include punny names implied by TDD principle. Quickstart scenarios include playful validation steps.

### II. TUI-First Experience
✅ **PASS** - ViewportState model ensures <50ms response (constitution) by rendering only visible lines. LazyFileContent prevents blocking on 100-file load. All latencies measured via Textual pilot in automated tests.

### III. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - Phase 1 created 3 contract documents (parser, performance, UI) defining 20+ test scenarios. Quickstart.md maps to 9 integration test scenarios. All tests must exist before implementation (contracts → failing tests → implementation).

### IV. Performance Within Constraints
✅ **PASS** - PerformanceBenchmark model enforces PRD limits programmatically. ViewportState + LazyFileContent architecture directly implements lazy loading (FR-005) and viewport rendering (FR-003). Hard 10k line limit (FR-002a) prevents exceeding PRD scale.

### V. Data Integrity Over Convenience
✅ **PASS** - DiffHunk.raw_text preserves malformed content (no data loss per FR-011). Comment preservation on parse errors specified in parser-contracts.md Scenario 1. Git metadata already integrated (M4). Line number accuracy maintained.

### VI. Graceful Degradation
✅ **PASS** - MalformedHunkError caught internally (never crashes user). DiffTooLargeError provides helpful error modal with exit path. Binary file placeholder ("No reviewable files") designed. I/O error recovery modal reuses M4 pattern (FR-010).

**Post-Design Gate Result**: ✅ PASS - Design artifacts (data model, contracts, quickstart) uphold all constitutional principles. No violations introduced.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
racgoat/
├── parser/
│   ├── models.py           # DiffHunk, DiffFile, DiffSummary (enhance for error handling)
│   └── diff_parser.py      # Core parser (add malformed hunk detection, line limit check)
├── ui/
│   ├── widgets/
│   │   ├── FilesPane.py    # File list (add lazy loading, viewport support)
│   │   ├── DiffPane.py     # Diff display (viewport rendering, malformed hunk markers)
│   │   └── TwoPaneLayout.py
│   └── models.py           # UI state models
├── services/
│   ├── comment_store.py    # Comment storage
│   ├── markdown_writer.py  # Output serialization
│   └── git_metadata.py     # Git context extraction
├── models/
│   └── comments.py         # Comment domain models
└── main.py                 # RacGoatApp (add size limit validation)

tests/
├── contract/
│   ├── test_binary_filtering.py  # REWRITE as TUI tests (FR-020)
│   ├── test_viewport_rendering.py  # NEW: viewport contract tests
│   └── test_error_handling.py      # NEW: malformed diff contracts
├── integration/
│   ├── test_milestone2/    # Existing TUI tests
│   ├── test_milestone5/    # Existing feature tests
│   └── test_performance/   # NEW: automated performance benchmarks (FR-013)
└── unit/
    ├── test_diff_parser.py  # Enhance with malformed hunk tests
    └── test_lazy_loading.py # NEW: lazy load unit tests

scripts/
└── generate_large_diff.py  # Existing perf test data generator
```

**Structure Decision**: Single project (TUI application). Existing structure extended with performance infrastructure (viewport rendering in DiffPane, lazy loading in FilesPane), error handling enhancements (parser malformed hunk detection), and test rewrites (binary filtering → TUI tests, new performance benchmarks).

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **From parser-contracts.md** (Error Handling & Size Limits):
   - Task: Extend DiffHunk model with `is_malformed`, `raw_text`, `parse_error` fields [P]
   - Task: Write contract test `test_malformed_hunk_detection` (invalid header, mismatched counts, mixed hunks)
   - Task: Implement malformed hunk try/catch in `diff_parser.py` → make test pass
   - Task: Extend DiffSummary with `total_line_count`, `exceeds_limit` [P]
   - Task: Write contract test `test_size_limit_enforcement` (under, at, over 10k lines)
   - Task: Implement line counting + DiffTooLargeError in parser → make test pass
   - Task: Rewrite `test_binary_filtering.py` as TUI tests (FilesPane assertions, not exit assertions)

2. **From performance-contracts.md** (Benchmarks & Viewport):
   - Task: Create ViewportState model [P]
   - Task: Create LazyFileContent model [P]
   - Task: Create PerformanceBenchmark model [P]
   - Task: Write contract test `test_initial_load_time` (small/medium/large diffs)
   - Task: Write contract test `test_file_switch_latency` (LazyFileContent materialization)
   - Task: Write contract test `test_scroll_responsiveness` (viewport rendering)
   - Task: Write contract test `test_comment_addition_latency`
   - Task: Refactor DiffPane from Static to VerticalScroll with viewport rendering → make tests pass
   - Task: Implement LazyFileContent in FilesPane.on_file_selected() → make tests pass
   - Task: Add pytest-benchmark integration to test suite [P]

3. **From ui-contracts.md** (Consistency & Error Display):
   - Task: Write contract test `test_keybinding_format_consistency` (grep for Ctrl/^/Control patterns)
   - Task: Write contract test `test_error_message_theme` (emoji bookends, helpful text)
   - Task: Write contract test `test_help_text_terminology` (canonical terms: "search mode", "Add comment")
   - Task: Audit all UI text with grep + manual review → fix inconsistencies → make tests pass
   - Task: Standardize error modals (DiffTooLargeError, I/O error recovery) → make tests pass
   - Task: Add visual indicator for malformed hunks in DiffPane (`[⚠ UNPARSEABLE]` prefix)

4. **From quickstart.md** (Integration Scenarios):
   - Task: Write integration test `test_large_diff_performance` (Scenario 1: 100 files/10k lines <2s)
   - Task: Write integration test `test_viewport_scrolling` (Scenario 2: 1000 line file smooth scroll)
   - Task: Write integration test `test_malformed_diff_handling` (Scenario 3: mixed valid/malformed)
   - Task: Write integration test `test_size_limit_error_modal` (Scenario 4: >10k rejection)
   - Task: Write integration test `test_binary_file_exclusion_tui` (Scenario 5: TUI list exclusion)
   - Task: Write integration test `test_io_error_recovery_modal` (Scenario 8: permission denied)
   - Task: Write integration test `test_end_to_end_workflow` (Scenario 9: full review cycle)

5. **From data-model.md** (New Entities):
   - Task: Extend DiffHunk model (fields: is_malformed, raw_text, parse_error) [P]
   - Task: Extend DiffFile model (fields: total_lines, has_malformed_hunks) [P]
   - Task: Extend DiffSummary model (fields: total_line_count, exceeds_limit) [P]
   - Task: Create ViewportState model [P] (duplicate of perf task, merge)
   - Task: Create LazyFileContent model [P] (duplicate of perf task, merge)
   - Task: Create PerformanceBenchmark model [P] (duplicate of perf task, merge)
   - Task: Create DiffTooLargeError exception class [P]
   - Task: Create MalformedHunkError exception class [P]

**Ordering Strategy** (TDD Compliance):

**Phase A: Models & Exceptions** (Parallel [P])
1. Extend parser models (DiffHunk, DiffFile, DiffSummary) - 3 tasks [P]
2. Create UI models (ViewportState, LazyFileContent) - 2 tasks [P]
3. Create error models (PerformanceBenchmark, exceptions) - 3 tasks [P]

**Phase B: Contract Tests** (Sequential, depends on models)
4. Parser contract tests (malformed hunks, size limits, binary TUI rewrite) - 3 tasks
5. Performance contract tests (load, switch, scroll, comment benchmarks) - 4 tasks
6. UI contract tests (keybinding, errors, help text, consistency) - 4 tasks

**Phase C: Implementation** (Make tests pass, sequential)
7. Parser error handling (malformed hunk detection, line counting) - 2 tasks
8. Viewport rendering (DiffPane refactor to VerticalScroll) - 1 task
9. Lazy loading (LazyFileContent integration) - 1 task
10. UI consistency fixes (text audit, error modal standardization) - 2 tasks

**Phase D: Integration Tests** (Depends on implementation, can be parallel within phase)
11. Integration test suite (7 scenarios from quickstart.md) - 7 tasks [P within phase]

**Phase E: Polish & Validation**
12. pytest-benchmark setup - 1 task [P]
13. Run full test suite validation - 1 task
14. Performance baseline measurement - 1 task

**Estimated Output**: ~35-40 numbered, ordered tasks in tasks.md

**Task Naming Convention** (TDD + Fun):
- Contract tests: "🦝 Test: [behavior] (contract)" (e.g., "🦝 Test: Malformed hunk displays raw text (contract)")
- Implementation: "🐐 Implement: [feature]" (e.g., "🐐 Implement: Viewport rendering in DiffPane")
- Integration: "🦝🐐 E2E: [scenario]" (e.g., "🦝🐐 E2E: Large diff loads under 2s")

**Dependency Markers**:
- [P] = Parallel (no dependencies within phase)
- [DEPENDS: Task #] = Sequential (wait for specific task)
- [BLOCKS: Feature] = Blocker for downstream work

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none - no violations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
