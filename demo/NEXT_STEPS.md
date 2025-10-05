# 🎯 Next Steps for Contest Submission

## ✅ Demo Materials Created

Your `/demo` directory now contains:

- ✅ **sample.diff** - Realistic authentication diff for demos
- ✅ **demo.tape** - VHS script for automated GIF creation
- ✅ **run_demo.sh** - Interactive demo generator
- ✅ **CONTEST_SUBMISSION.md** - Polished submission text
- ✅ **README.md** - Demo instructions
- ✅ **SCREENSHOT_GUIDE.md** - How to take screenshots
- ✅ **INSTALL_TOOLS.md** - Tool installation guide

## 🎬 Choose Your Demo Method

### Option A: Automated GIF (Best)

**Install VHS:**
```bash
# macOS
brew install vhs

# Linux (requires Go)
go install github.com/charmbracelet/vhs@latest
```

**Generate GIF:**
```bash
cd /home/jjshanks/workspace/racgoat
vhs demo/demo.tape
```

**Output:** `demo/racgoat-demo.gif` (~30-60 seconds)

---

### Option B: Manual Recording

**Install tools:**
```bash
pip install asciinema
cargo install --git https://github.com/asciinema/agg
```

**Record:**
```bash
./demo/run_demo.sh
# Choose option 2
```

---

### Option C: Screenshots (Quickest)

Follow the guide in `demo/SCREENSHOT_GUIDE.md`:

1. Run: `cat demo/sample.diff | uv run python -m racgoat -o demo/review.md`
2. Take 5 screenshots:
   - Main TUI view
   - Comment marker
   - Help overlay
   - Search feature
   - Markdown output
3. Save as `01-main-view.png`, `02-comment-marker.png`, etc.

---

## 📝 Update Your Submission

### 1. Test the Demo Manually

Make sure everything works:

```bash
# Test the sample diff
cat demo/sample.diff | uv run python -m racgoat -o demo/review.md

# Navigate, add comments, search, show help, quit
# Then check the output:
cat demo/review.md
```

### 2. Add Visuals to README

Once you have your GIF or screenshots:

**For GIF:**
```markdown
## 🎬 Demo

![RacGoat Demo](demo/racgoat-demo.gif)
```

**For screenshots:**
```markdown
## 🎬 Screenshots

### Two-Pane TUI
![Main View](demo/01-main-view.png)

### Help Overlay
![Help](demo/03-help-overlay.png)

### Markdown Output
![Output](demo/05-markdown-output.png)
```

Add this section near the top of your main `README.md`.

### 3. Update Contest Submission

Use the text from `demo/CONTEST_SUBMISSION.md`:

**Where to post:** Discord #share-your-project (by October 7)

**Required info:**
- ✅ How you built it (slash commands, Claude Code workflow)
- ✅ Screenshots or demos (GIF/screenshots/video)
- ✅ Must be your own work, built with Claude Sonnet 4.5

**Template ready:** Copy from `demo/CONTEST_SUBMISSION.md`

### 4. Add Missing Elements

**GitHub repo URL:**
- Replace `[Add your repo URL]` in CONTEST_SUBMISSION.md
- Make sure repo is public

**Badge (optional):**
Add to top of README.md:
```markdown
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20Sonnet%204.5-5A67D8)](https://claude.ai)
```

---

## 🎨 Polish Your GitHub Repo

Before submitting:

### Essential
- [ ] Add demo GIF or screenshots to README
- [ ] Verify all installation instructions work
- [ ] Test: `uv tool install .` works
- [ ] Repository is public
- [ ] LICENSE file exists (MIT)

### Nice to Have
- [ ] Add demo GIF to top of README
- [ ] Add "Built with Claude" badge
- [ ] Clean up any TODOs or WIP comments
- [ ] Run full test suite: `uv run pytest`
- [ ] Tag release: `git tag v1.0.0`

---

## 🚀 Submit to Contest

**Deadline:** October 7

**Steps:**
1. Go to Discord #share-your-project
2. Create a new post with:
   - Title: "RacGoat: AI Code Review TUI 🦝🐐"
   - Copy text from `demo/CONTEST_SUBMISSION.md`
   - Attach GIF/screenshots
   - Add GitHub repo link
3. Mention features: "Built 100% with Claude Sonnet 4.5 using custom slash commands"
4. Engage with comments/questions

**Target award:** "Keep Coding" (most technically impressive)

**Backup awards:**
- "Keep Creating" (artistic use - raccoon/goat theme)
- Could argue for "Keep Learning" (demonstrates AI dev workflow)

---

## 📋 Quick Checklist

Before submitting:

**Demo materials:**
- [ ] Created GIF or 5 screenshots
- [ ] Tested manual demo to verify it works
- [ ] Visuals show all key features

**Documentation:**
- [ ] Added demo to README.md
- [ ] GitHub repo is public
- [ ] Repo URL added to submission text
- [ ] LICENSE file exists

**Contest post:**
- [ ] Copied text from CONTEST_SUBMISSION.md
- [ ] Attached visuals (GIF or screenshots)
- [ ] Posted by October 7
- [ ] Included GitHub link

---

## 🎯 Recommended Priority

**If you have 30 minutes:**
1. Take 5 screenshots (see SCREENSHOT_GUIDE.md)
2. Add to README
3. Post to Discord with CONTEST_SUBMISSION.md text

**If you have 2 hours:**
1. Install VHS: `brew install vhs`
2. Generate GIF: `vhs demo/demo.tape`
3. Add to README at top
4. Polish submission text
5. Post to Discord

**If you have 1 day:**
1. Do the 2-hour version
2. Record a 1-2 min video walkthrough
3. Create comparison (before/after using RacGoat)
4. Write blog post about the meta-workflow
5. Share on Twitter/LinkedIn too

---

## 🆘 Need Help?

**Demo not working?**
- See troubleshooting in `demo/README.md`
- Try manual test first: `./demo/run_demo.sh` → option 3

**Tools won't install?**
- Use screenshot method instead
- Or record with phone pointed at screen

**Questions about submission?**
- Review contest rules: [link in Discord]
- Ask in #share-your-project

---

## 🎉 You're Ready!

All materials are prepared. Choose your demo method, create visuals, and submit!

**Good luck!** 🦝🐐

---

*"In code we trust, in raccoons we debug, in goats we climb."*
