# **AI Code Review TUI (v1)**

## Milestone 1: CLI Data Processor & Parser
**Goal**: Create a non-visual command-line tool that successfully ingests, parses, and summarizes a `git diff`. This validates the entire data input and processing pipeline without any UI complexity.

**Tasks**:
    * Implement logic to read a `git diff` from `stdin`.
    * Parse the diff data to identify changed files and count their added/removed lines.
    * Filter and skip binary, non-text, and specified generated files (e.g., `.lock`, `.min.js`).
    * Implement command-line argument parsing for the `-o <filename>` flag.
    * For this milestone, the tool's output will be a **simple text summary written to a file** (e.g., `path/to/file.py: +10 -5`). The output filename should be controllable via the `-o` flag.
    * Handle the edge case of an empty diff.

**Deliverable**: A runnable CLI that processes a diff and writes a summary of changed files and line counts to an output file.

## Milestone 2: TUI Rendering & Navigation
**Goal**: Build the read-only visual interface. This milestone takes the parsed data structure from Milestone 1 and renders it in an interactive TUI.

**Tasks**:
    * Build the basic two-pane TUI layout: a **Files Pane** on the left and a **Diff Pane** on the right.
    * Populate the file list using the parsed diff data.
    * Render the selected file's diff hunks in the Diff Pane with correct **ANSI color highlighting** and post-change line numbers.
    * Implement navigation: `arrow keys` to move within a pane and `Tab` to switch focus.
    * Implement the `q` key to quit the application.
    * Display a "No diff" message if the input was empty.

**Deliverable**: A read-only TUI diff viewer. Invoking the tool now opens the visual interface instead of writing a summary file.

## Milestone 3: Core Commenting Engine
**Goal**: Implement the primary user action: creating and storing feedback. This milestone focuses on adding, selecting, and managing comments in memory.

**Tasks**:
    * Design and implement the in-memory data structures for storing comments.
    * Implement adding a **single-line comment** (`a`), a **file-level comment** (`c`), and **range-based comments** via **Select Mode** (`s`).
    * Display a visual marker (`*`) in the Diff Pane to indicate comments.
    * Update the status bar to show context-sensitive keybindings for commenting.

**Deliverable**: An interactive TUI where a user can fully annotate a diff in-memory.

## Milestone 4: End-to-End Workflow & Markdown Output
**Goal**: Close the primary user loop by persisting the in-memory comments to the specified Markdown file upon exit.

**Tasks**:
    * On quit, implement the logic to serialize the stored comments into the specified Markdown format.
    * Write the formatted output to the file specified with the `-o` flag (or `review.md`).
    * Ensure no output file is generated if no comments were made.
    * Attempt to extract and include the current `branch name` and `commit sha` in the output header.

**Deliverable**: A complete, functional tool that produces the specified `review.md` artifact.

## Milestone 5: Advanced Interaction & Usability
**Goal**: Enhance the user experience with advanced features that make the review process more efficient.

**Tasks**:
    * Implement the comment **edit/delete** functionality (`e`).
    * Implement **search functionality** (`/`) within the diff view.
    * Create a **help overlay** (`?`) that displays all keybindings.

**Deliverable**: A feature-complete application that matches all interactive requirements from the PRD.

## Milestone 6: Performance Hardening & Final Polish
**Goal**: Ensure the application is robust, performant, and reliable, especially when handling large-scale code changes.

**Tasks**:
    * Implement **lazy loading** and **viewport rendering** to meet the 100 files / 10,000 lines performance requirement.
    * Benchmark the application against large, real-world diffs.
    * Add robust error handling for malformed diff inputs.
    * Refine all UI elements and help text for clarity and consistency.

**Deliverable**: A production-ready, performant, and stable **v1** of the AI Code Review TUI.
