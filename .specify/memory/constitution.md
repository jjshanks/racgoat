<!--
Sync Impact Report:
- Version Change: [NONE] → 1.0.0 (initial constitution)
- Modified Principles: N/A (new document)
- Added Sections: All (new document)
- Removed Sections: N/A
- Templates Requiring Updates:
  ✅ plan-template.md (already references constitution check)
  ✅ spec-template.md (no changes needed - tech-agnostic by design)
  ✅ tasks-template.md (already references TDD and constitution)
  ✅ agent-file-template.md (no changes needed - auto-generated)
- Follow-up TODOs: None
-->

# RacGoat Constitution

## Core Principles

### I. Fun Is a Feature (NON-NEGOTIABLE)
RacGoat MUST be delightful to use and maintain. Humor is not optional—it's core to the project's identity:
- Function names, docstrings, and comments embrace the raccoon/goat theme
- Easter eggs are encouraged (type "trash" for surprises)
- Test names MUST be both descriptive AND punny
- Error messages can be whimsical while remaining helpful
- Documentation should make people smile
- Code reviews should celebrate clever jokes alongside clean code
- If a feature isn't fun to build or use, question whether it belongs

**Rationale**: Developer tools don't have to be soulless. Joy makes the codebase maintainable, attracts contributors, and differentiates RacGoat from boring alternatives. A raccoon and a goat wouldn't settle for mundane—neither should we.

### II. TUI-First Experience
Every feature MUST enhance the terminal user interface experience. The application lives in the terminal and MUST:
- Render efficiently with minimal latency (<50ms response to user input)
- Work gracefully within standard terminal constraints (80x24 minimum)
- Use Textual framework patterns consistently across all widgets
- Support keyboard-only navigation (no mouse required)
- Maintain visual consistency with the raccoon/goat theme

**Rationale**: RacGoat is a TUI application. The terminal interface is the product, not a secondary concern. Users expect immediate responsiveness and keyboard efficiency in terminal tools.

### III. Test-Driven Development (NON-NEGOTIABLE)
TDD is MANDATORY for all features. The cycle MUST be:
1. Write tests that describe desired behavior (with punny names!)
2. Get user approval on test scenarios
3. Verify tests FAIL (red)
4. Implement minimum code to pass (green)
5. Refactor while keeping tests green (and keeping it fun)

**Rationale**: Given the complexity of TUI rendering, diff parsing, and comment state management, untested code will break. Tests are the specification. And they should be enjoyable to read.

### IV. Performance Within Constraints
The application MUST handle the PRD-specified scale without degradation:
- Up to 100 files in a single diff
- Up to 10,000 total diff lines
- Lazy loading and viewport rendering required for large diffs
- No blocking operations during user interaction
- File filtering (binary, generated files) happens at parse time

**Rationale**: Code review is already cognitively demanding. A sluggish tool compounds frustration. Performance targets are non-negotiable for user adoption.

### V. Data Integrity Over Convenience
Comment state and diff context MUST be preserved accurately:
- Line numbers are post-change and correctly prefixed (+/-)
- Comments map to exact line ranges or file scope
- Overlapping comments allowed (line + range on same position)
- Git metadata (branch, SHA) captured when available
- Output only generated if comments exist

**Rationale**: A code review tool that loses or misrepresents comments destroys trust. Accuracy is the foundation of the product's value. Even raccoons don't mess with trash they can't handle.

### VI. Graceful Degradation
The application MUST handle edge cases and errors without crashing:
- Empty diffs display "No diff" message, app remains open
- Malformed diffs trigger clear error messages (bonus points if they're funny)
- Missing git metadata leaves fields blank (doesn't abort)
- Unrecognized file types skipped with warning
- Invalid UTF-8 handled gracefully

**Rationale**: Real-world git diffs are messy. The tool must be robust enough to handle repository chaos without requiring perfect input. Goats climb rocky cliffs; RacGoat handles rocky code.

## Development Workflow

### Milestone-Based Delivery
Features MUST align with the roadmap in `docs/roadmap.md`:
- Each milestone is independently testable
- Milestones build sequentially (no skipping)
- User scenarios from PRD map to integration tests
- Milestone completion = all tests passing + PRD scenarios validated
- Celebrate milestone completion with a good pun

**Rationale**: The PRD defines a clear build sequence from CLI parser → TUI → commenting → output. Skipping steps creates untestable gaps.

### Code Review Requirements
All changes MUST:
- Pass pytest suite (no failing tests tolerated)
- Include tests for new behavior (with personality!)
- Update CLAUDE.md if architectural patterns change
- Follow Python 3.12+ idioms and type hints
- Maintain or improve Textual widget composition clarity
- Include at least one smile-inducing element (comment, name, or easter egg)

**Rationale**: The codebase is the team's communication medium. Consistent standards reduce cognitive load during reviews. Humor keeps reviewers engaged.

## Technology Constraints

### Python 3.12+ with UV
- Dependency management ONLY via UV (`uv add`, not pip/poetry)
- Type hints encouraged for public APIs
- No dependencies that conflict with Textual's event loop
- Prefer standard library where Textual doesn't provide equivalent

**Rationale**: UV is fast and reproducible. Python 3.12+ unlocks modern syntax. Dependency discipline prevents version hell.

### Textual Framework
- Widget composition via `compose()` method
- Event handlers follow `on_*` naming convention
- CSS styling via class variables
- Keybindings via BINDINGS class variable
- No direct terminal manipulation (let Textual handle rendering)

**Rationale**: Textual provides the TUI abstraction. Fighting the framework creates bugs. Consistency with Textual patterns makes the codebase learnable.

## Governance

### Amendment Process
Constitution changes require:
1. Clear justification for the change (why current principle blocks progress)
2. Proposed new/modified principle text
3. Impact analysis on existing code/plans
4. Approval before implementation proceeds
5. A good reason why the change makes RacGoat better/more fun

### Versioning Policy
- **MAJOR**: Principle removal or redefinition that invalidates prior decisions
- **MINOR**: New principle added or existing principle materially expanded
- **PATCH**: Clarifications, wording fixes, non-semantic improvements

### Compliance Review
- All feature specs (`/specify`) command checks against constitution
- All implementation plans (`/plan`) include Constitution Check section
- Task generation (`/tasks`) respects TDD ordering and principle-driven requirements
- Violations MUST be documented in Complexity Tracking with justification
- The "Fun Is a Feature" principle applies to all governance processes

**Version**: 1.0.0 | **Ratified**: 2025-09-30 | **Last Amended**: 2025-09-30
