<!--
Sync Impact Report - Constitution Update
═══════════════════════════════════════

Version Change: Template → 1.0.0
Type: MAJOR (initial constitution ratification)

Principle Changes:
  ADDED: I. TUI-First Architecture
  ADDED: II. Test-Driven Development (NON-NEGOTIABLE)
  ADDED: III. Performance Contracts
  ADDED: IV. Playful Professionalism
  ADDED: V. Milestone-Based Development

Section Changes:
  ADDED: Technical Standards
  ADDED: Development Workflow
  ADDED: Governance

Template Synchronization Status:
  ✅ plan-template.md - Constitution Check section aligned
  ✅ spec-template.md - User scenario testing aligns with TDD principle
  ✅ tasks-template.md - Test-first pattern matches principle II
  ⚠️  No agent-specific command references detected requiring updates

Follow-up TODOs:
  - None (all placeholders filled)

Rationale:
  MAJOR version justified because this is the initial constitution
  establishing core governance for the RacGoat project. All principles
  derived from existing project patterns: Textual TUI framework, pytest
  test-first workflow, performance benchmarks in PRD, raccoon/goat theme,
  and milestone-driven specs/.
-->

# RacGoat Constitution

## Core Principles

### I. TUI-First Architecture

RacGoat is fundamentally a Terminal User Interface application built on the Textual framework. All features MUST integrate with the TUI paradigm and keyboard-driven interaction model.

**Rules:**
- New features MUST be accessible via keyboard bindings (no mouse required)
- UI components MUST extend Textual widgets (Static, VerticalScroll, Container, etc.)
- State management MUST use Textual's reactive properties and message passing
- Visual feedback MUST use ANSI colors and text-based indicators
- Performance MUST support real-time rendering without blocking the event loop

**Rationale:** RacGoat exists to provide an efficient, keyboard-driven code review workflow. Breaking the TUI paradigm would undermine the core product value and introduce complexity (GUI frameworks, web servers) that violates project scope.

### II. Test-Driven Development (NON-NEGOTIABLE)

Tests are written BEFORE implementation. All features proceed via the Red-Green-Refactor cycle: write failing tests, get user/stakeholder approval, then implement to pass.

**Rules:**
- Contract tests (tests/contract/) MUST validate PRD requirements
- Integration tests (tests/integration/) MUST validate end-to-end TUI workflows
- Unit tests (tests/unit/) MUST validate individual components in isolation
- Tests MUST fail before the feature implementation begins
- Code without tests MUST NOT be merged (exceptions require explicit approval and justification)
- Performance benchmarks MUST be validated in tests/integration/test_performance/

**Rationale:** TDD ensures RacGoat maintains reliability and prevents regression. The three-tier test structure (contract/integration/unit) provides clear boundaries: PRD compliance, user journey validation, and component correctness. This is non-negotiable because TUI bugs are difficult to debug interactively.

### III. Performance Contracts

RacGoat MUST handle up to 100 files and 10,000 diff lines with specific latency guarantees defined in the PRD.

**Rules:**
- Initial load MUST complete in <2 seconds (100 files, 10k lines)
- Scroll operations MUST complete in <100ms
- Search operations MUST complete in <200ms (2000 line files)
- Comment edit operations MUST complete in <100ms (100+ comments)
- Markdown serialization MUST complete in <5s (100 comments)
- File write MUST complete in <1s
- Performance tests MUST validate these contracts before release
- Violations MUST be justified with profiling data and documented as technical debt

**Rationale:** Code review efficiency depends on responsiveness. Users will abandon a slow TUI. These contracts were derived from PRD requirements and validated in Milestone 6 performance hardening. Viewport rendering and lazy loading are architectural consequences of these contracts.

### IV. Playful Professionalism

RacGoat embraces a raccoon (resourceful, clever) + goat (determined, persistent) theme throughout code, documentation, and user-facing messages. This theme MUST be balanced with professional functionality.

**Rules:**
- Function names SHOULD include theme references where natural (e.g., `goat_climb`, `raccoon_cache`)
- Docstrings MUST include puns or thematic language WITHOUT sacrificing clarity
- User-facing messages MUST be friendly and thematic (e.g., "No diff to review - the raccoons found nothing!")
- Test names MUST be descriptive AND punny where possible
- Theme elements MUST NOT obscure technical intent or debugging
- Easter eggs are encouraged but MUST NOT interfere with core functionality

**Rationale:** The theme differentiates RacGoat from generic code review tools and makes development enjoyable. However, this is a professional tool first - readability and debuggability supersede cleverness. The theme adds personality without compromising technical rigor.

### V. Milestone-Based Development

Features are implemented through structured milestones (specs/###-feature-name/) with clear specifications, plans, and task lists.

**Rules:**
- Each milestone MUST have a spec.md defining user scenarios and requirements
- Implementation MUST follow the /speckit workflow (specify → plan → tasks → implement)
- Specifications MUST be technology-agnostic (no implementation details)
- Plans MUST define concrete technical approach with file paths
- Tasks MUST be organized by user story priority (P1, P2, P3...)
- Each milestone MUST be independently testable and deliverable
- Cross-milestone dependencies MUST be explicitly documented

**Rationale:** Structured milestones enable clear progress tracking, prioritization, and rollback. RacGoat evolved through 7 milestones (M1-M7: parsing → TUI → commenting → output → editing/search → performance → enhanced output). This approach reduces scope creep and ensures each feature is fully specified before implementation.

## Technical Standards

### Language and Dependencies

- **Python Version:** 3.12+ (set in .python-version)
- **Package Manager:** UV (not pip/poetry)
- **TUI Framework:** Textual (primary dependency)
- **Testing Framework:** pytest
- **Type Hints:** Encouraged (Python 3.12+ features allowed)
- **Docstring Style:** Google style with playful tone

### Error Handling

- Malformed diff hunks MUST display `[⚠ UNPARSEABLE]` visual indicator
- Oversized diffs (>10k lines) MUST show error modal and gracefully exit
- File write failures MUST show error recovery modal
- All exceptions MUST be caught at TUI boundaries to prevent crashes
- Error messages MUST be user-friendly and actionable

### Code Organization

- Parser models: racgoat/parser/models.py (DiffHunk, DiffFile, DiffSummary)
- UI widgets: racgoat/ui/widgets/ (FilesPane, DiffPane, StatusBar, etc.)
- Comment models: racgoat/models/comments.py (Comment, CommentTarget, etc.)
- Services: racgoat/services/ (comment_store, markdown_writer, git_metadata)
- Tests: tests/contract/, tests/integration/, tests/unit/

### Git Workflow

- Branch naming: `###-feature-name` (e.g., `007-currently-the-review`)
- Commits MUST use episodic story format with /ep-commit command
- PRD requirements MUST be validated via contract tests before merge
- Milestone completion MUST update CLAUDE.md and README.md status sections

## Development Workflow

### Before Starting Work

1. Read PRD (docs/prd.md) and relevant milestone spec (specs/###-feature-name/spec.md)
2. Verify constitution compliance (no violations without justification)
3. Understand test categories: contract (PRD), integration (workflow), unit (components)

### During Development

1. Write tests FIRST (contract → integration → unit as needed)
2. Verify tests FAIL before implementing
3. Implement feature following plan.md file paths
4. Run test suite: `uv run pytest`
5. Update CLAUDE.md milestone status when complete
6. Commit with episodic story format using /ep-commit

### Before Merging

1. All contract tests MUST pass (validates PRD compliance)
2. All integration tests MUST pass (validates user workflows)
3. All unit tests MUST pass (validates components)
4. Performance contracts MUST be validated (if applicable)
5. README.md and CLAUDE.md MUST reflect current status
6. Constitution violations MUST be justified and documented

## Governance

**Authority:** This constitution supersedes all other development practices. When in conflict, constitution principles take precedence.

**Compliance:** All PRs, code reviews, and architecture decisions MUST verify alignment with these principles. Violations require explicit justification in the Complexity Tracking section of plan.md.

**Amendments:** Constitution changes require:
1. Documented rationale (why current principle is insufficient)
2. Approval from project maintainer
3. Migration plan for affected code/templates
4. Version bump following semantic versioning (MAJOR for backward-incompatible changes, MINOR for additions, PATCH for clarifications)
5. Sync Impact Report documenting template changes

**Review Cadence:** Constitution compliance is reviewed at each milestone completion. Principles may be refined based on lessons learned, but core non-negotiables (TDD, Performance Contracts) require extraordinary justification to change.

**Runtime Guidance:** For AI coding assistants (e.g., Claude Code), refer to CLAUDE.md for architecture patterns, development commands, and milestone roadmap. The constitution defines "what" and "why"; CLAUDE.md defines "how".

---

**Version**: 1.0.0 | **Ratified**: 2025-10-10 | **Last Amended**: 2025-10-10
