# PRD: AI Code Review TUI (v1)

## 1. Product Goal

A command-line TUI that allows a software engineer to efficiently review AI-generated `git diffs` and create a structured feedback document that can be fed back to the AI agent for code correction.

## 2. User Workflow

1. **Invocation**:

   The user pipes a `git diff` into the application via **stdin** (e.g., `git diff HEAD~1 | review-tool`). Optionally, use the `-o <filename>` flag to specify a custom output file (defaults to `review.md`).

2. **Review**:

   * The TUI displays a two-pane view: a list of changed files on the left and the selected file’s diff on the right.
   * The diff shows only changed hunks with context lines.
   * Users navigate through the files and diffs, adding comments line-by-line, on ranges of lines, or for an entire file.
   * Only one comment can exist per line/range, but overlapping scopes are allowed (e.g., a range comment on `10–15` plus a single-line comment on `12`).
   * A marker (`*`) indicates where a comment exists.
   * If the diff is empty, the app stays open with a “No diff” message in the main area.
   * Binary, non-text, and generated files (e.g., `.lock`, `.min.js`) are skipped/collapsed. UTF-8 encoding is assumed.

3. **Export**:

   * On quit, the application generates a Markdown file containing all review comments (saved to `review.md` by default or the specified file via `-o`).
   * Files without comments are not included in the output.
   * If no comments exist, no output file is generated.

## 3. Core Features & Keybindings
* **UI Layout**:

  * **Files Pane**: Navigable list of changed files (excluding skipped files).
  * **Diff Pane**: Diff content for the selected file, showing only changed hunks with context lines and **green (+)** and **red (-)** highlighting for additions and deletions (ANSI colors assumed). Line numbers are post-change.
  * **Status Bar**: Footer showing context-sensitive help (e.g., “Arrows: Navigate | Tab: Switch panes | s: Select | a: Add comment | c: File comment | e: Edit comments | /: Search | ?: Help | q: Quit”).

* **Navigation and Focus**:

  * `arrow keys`: Navigate the focused pane.
  * `Tab`: Switch focus between files and diff.

* **Commenting Actions**:

  * `s`: Enter **Select Mode** to highlight a multi-line range.
  * `a`: Add a comment to the current line or selection.
  * `c`: Add an overall **Comment** for the entire file.
  * `e`: Edit/delete comments for the current file (popup with positions + previews on the left, full text on the right).
  * Editing is limited to the current file; reassigning scope (line vs. range vs. file) is not supported.

* **State Management**:

  * `Enter`: Save current comment.
  * `Esc`: Return to normal navigation mode.
  * `q`: Quit and generate output.

* **Performance**:

  * Support up to **100 files** and **10,000 total diff lines**.
  * Use lazy loading and viewport rendering for efficiency.

* **Reserved Keys**:

  * `/`: Search within the current diff.
  * `?`: Display help overlay.

## 4. Output Specification

The tool outputs a single Markdown file formatted as follows (only if comments exist):

```markdown
<branch name> <commit sha>

# <file path>
<overall comment if provided>
<line>: <comment>
<line-range>: <comment>
...

```
* Line numbers/ranges are post-change, prefixed with `+` for added lines, `-` for removed lines (e.g., `+123`, `-45-47`).
* Unchanged context lines have no prefix.
* Files with no comments are omitted.
* If branch name/commit SHA cannot be determined, fields may be left blank.

## 5. Out of Scope (v1)

* **No Platform Integration**: Local-only; no GitHub/GitLab integration.
* **Single Output Format**: Markdown only.
* **No Direct Git Operations**: The tool does not stage, commit, or manage branches.
* **Configurable Keybindings**: Not supported in v1.
* **Advanced File Filtering**: Only binary/non-text/generated files skipped.
