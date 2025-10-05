# RacGoat v1.0.0 Release Checklist 🦝🐐

This document provides a step-by-step guide for releasing RacGoat v1.0.0 to GitHub and PyPI.

## 📋 Pre-Release Checklist

### ✅ Documentation & Configuration (COMPLETED)

- [x] Enhanced `pyproject.toml` with PyPI metadata
  - [x] Added authors, keywords, classifiers
  - [x] Added project URLs (homepage, repository, issues, changelog)
  - [x] Verified license field
- [x] Created `CONTRIBUTING.md` with development guidelines
- [x] Created `CHANGELOG.md` with v1.0.0 release notes
- [x] Updated `README.md` with badges and PyPI installation
- [x] Created `.github/workflows/test.yml` for CI
- [x] Created `.github/workflows/publish.yml` for PyPI publishing
- [x] Created GitHub issue templates (bug report, feature request)
- [x] Created pull request template
- [x] Updated `.gitignore` to exclude build artifacts
- [x] Verified package builds successfully (`uv build`)

### 🧪 Testing & Quality Assurance

Before proceeding with the release, verify:

- [ ] **Run full test suite**:
  ```bash
  uv run pytest -v
  ```
  - Expected: All tests pass (or document known issues)
  - Note: Some performance tests may need cleanup (see CLAUDE.md)

- [ ] **Run contract tests specifically**:
  ```bash
  uv run pytest tests/contract/ -v
  ```
  - Expected: 42+ contract tests passing

- [ ] **Test package installation locally**:
  ```bash
  # Build the package
  uv build

  # Install in a temporary environment
  uv tool install dist/racgoat-1.0.0-py3-none-any.whl

  # Test the CLI
  racgoat --help
  echo "test" | racgoat

  # Uninstall
  uv tool uninstall racgoat
  ```

- [ ] **Verify all documentation links work**:
  - Check README.md links
  - Check CONTRIBUTING.md links
  - Verify CHANGELOG.md formatting

## 🚀 Release Steps

### Phase 1: GitHub Repository Setup

1. **Create GitHub repository** (if not already created):
   - Go to https://github.com/new
   - Repository name: `racgoat`
   - Description: "A TUI app for reviewing git diffs - part raccoon mischief, part goat stubbornness 🦝🐐"
   - Public repository
   - Do NOT initialize with README (we already have one)

2. **Configure repository settings**:
   - **About section**:
     - Description: "A TUI app for reviewing git diffs - part raccoon mischief, part goat stubbornness 🦝🐐"
     - Website: (leave empty for now)
     - Topics: `tui`, `python`, `textual`, `code-review`, `diff`, `cli`, `terminal`, `git`
   - **Features**:
     - ✓ Issues
     - ✓ Discussions (optional but recommended)
     - ✓ Preserve this repository

3. **Push code to GitHub**:
   ```bash
   # Add remote (if not already added)
   git remote add origin https://github.com/jjshanks/racgoat.git

   # Verify current branch
   git branch

   # Push main branch
   git push -u origin main

   # Verify on GitHub that all files are there
   ```

4. **Wait for first CI run to complete**:
   - Go to Actions tab
   - Verify test workflow runs successfully
   - Fix any issues before proceeding

### Phase 2: PyPI Setup & Configuration

5. **Create PyPI account** (if you don't have one):
   - Go to https://pypi.org/account/register/
   - Verify email address

6. **Configure Trusted Publishing on PyPI**:
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name**: `racgoat`
     - **Owner**: `jjshanks`
     - **Repository name**: `racgoat`
     - **Workflow name**: `publish.yml`
     - **Environment name**: `pypi`
   - Click "Add"
   - Note: The project doesn't need to exist yet for pending publishers

7. **Create GitHub Environment** (for publish workflow):
   - Go to repository Settings → Environments
   - Click "New environment"
   - Name: `pypi`
   - Optional: Add protection rules (require reviewers for production)
   - Click "Configure environment"

### Phase 3: Create and Push Release Tag

8. **Final pre-release verification**:
   ```bash
   # Clean build artifacts
   just clean  # or: find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

   # Verify tests pass
   uv run pytest tests/unit/ -v

   # Rebuild package
   uv build

   # Verify version in built package
   ls -lh dist/
   # Should see: racgoat-1.0.0.tar.gz and racgoat-1.0.0-py3-none-any.whl
   ```

9. **Commit any final changes**:
   ```bash
   git status
   git add .
   git commit -m "chore: prepare for v1.0.0 release"
   git push origin main
   ```

10. **Create and push the release tag**:
    ```bash
    # Create annotated tag
    git tag -a v1.0.0 -m "Release v1.0.0 - The Champion of Syntaxia"

    # Verify tag
    git tag -l
    git show v1.0.0

    # Push tag to GitHub (this triggers the publish workflow!)
    git push origin v1.0.0
    ```

### Phase 4: Monitor Release Process

11. **Monitor GitHub Actions**:
    - Go to Actions tab on GitHub
    - Find the "Publish to PyPI" workflow run
    - Watch the progress:
      - ✓ Tests run
      - ✓ Package builds
      - ✓ PyPI publish completes
      - ✓ GitHub Release created

12. **Verify PyPI publication**:
    - Go to https://pypi.org/project/racgoat/
    - Verify version 1.0.0 is published
    - Check that README renders correctly
    - Verify metadata (links, classifiers, keywords)

13. **Verify GitHub Release**:
    - Go to https://github.com/jjshanks/racgoat/releases
    - Verify v1.0.0 release is created
    - Check release notes
    - Verify artifacts (wheel and sdist) are attached

### Phase 5: Post-Release Verification

14. **Test installation from PyPI**:
    ```bash
    # Install from PyPI
    uv tool install racgoat

    # Verify it works
    racgoat --help

    # Test with a real diff
    git diff HEAD~1 | racgoat -o test_review.md

    # Check the output
    cat test_review.md

    # Clean up
    rm test_review.md
    ```

15. **Test installation methods from README**:
    ```bash
    # Test pipx installation
    pipx install racgoat
    racgoat --help
    pipx uninstall racgoat

    # Test pip installation
    pip install racgoat
    racgoat --help
    pip uninstall racgoat
    ```

16. **Update README badge (if needed)**:
    - PyPI version badge should now show v1.0.0
    - If using shields.io badges, they update automatically

## 📢 Post-Release Activities

### Announcements

17. **Create announcement** (optional):
    - [ ] Post to GitHub Discussions (if enabled)
    - [ ] Share on relevant communities (Reddit, Hacker News, etc.)
    - [ ] Tweet/social media (if desired)

### Monitoring

18. **Monitor for issues**:
    - [ ] Watch GitHub Issues for bug reports
    - [ ] Check PyPI download stats after a few days
    - [ ] Respond to any installation issues quickly

### Documentation Updates

19. **Update any external documentation**:
    - [ ] Personal website/portfolio (if applicable)
    - [ ] Project showcase sites (if listed)

## 🐛 Troubleshooting

### If PyPI publish fails:

1. **Check GitHub Actions logs** for detailed error messages
2. **Verify trusted publishing setup**:
   - Environment name matches (`pypi`)
   - Repository and workflow names are correct
3. **Check PyPI project name** isn't already taken
4. **Verify package metadata** is valid (run `uv build` locally first)

### If tests fail in CI:

1. **Run tests locally** to reproduce
2. **Check for environment-specific issues** (Windows/macOS vs Linux)
3. **Fix issues and create a new patch release** (v1.0.1)

### If installation from PyPI fails:

1. **Verify package contents**:
   ```bash
   # Download and inspect
   pip download racgoat
   tar -tzf racgoat-1.0.0.tar.gz | head -20
   ```
2. **Check dependency versions** in pyproject.toml
3. **Test in a clean environment**

## 📝 Post-Release Checklist

After successful release:

- [ ] All installation methods work (uv, pip, pipx)
- [ ] PyPI page looks correct
- [ ] GitHub release is published
- [ ] Badges in README show correct version
- [ ] Tests pass on all platforms (via CI)
- [ ] Documentation links work
- [ ] Issue templates are available

## 🎉 Success Criteria

The release is successful when:

1. ✅ Package is published on PyPI at https://pypi.org/project/racgoat/1.0.0/
2. ✅ GitHub release is created at https://github.com/jjshanks/racgoat/releases/tag/v1.0.0
3. ✅ Users can install via `uv tool install racgoat`
4. ✅ CLI works: `racgoat --help` shows usage
5. ✅ End-to-end workflow works: diff → review → markdown output
6. ✅ Tests pass in CI on all platforms
7. ✅ No critical bugs reported in first 24 hours

## 🦝🐐 Congratulations!

Once all steps are complete, RacGoat v1.0.0 is officially released!

May your code reviews be thorough, your bugs be few, and your commits be clean! 🎉

---

*"In code we trust, in raccoons we debug, in goats we climb."* - Ancient RacGoat Proverb
