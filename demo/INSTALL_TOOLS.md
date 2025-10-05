# Installing Demo Tools

Choose one method to create your demo GIF:

## Option 1: VHS (Recommended - Automated)

VHS creates automated terminal recordings from scripts. Best for polished, reproducible demos.

### macOS
```bash
brew install vhs
```

### Linux (requires Go)
```bash
# Install Go first if needed
# Then:
go install github.com/charmbracelet/vhs@latest

# Make sure Go bin is in PATH
export PATH="$PATH:$(go env GOPATH)/bin"
```

### Verify
```bash
vhs --version
```

### Run Demo
```bash
cd /home/jjshanks/workspace/racgoat
vhs demo/demo.tape
# Output: demo/racgoat-demo.gif
```

---

## Option 2: asciinema + agg (Manual Recording)

Record yourself using the app, then convert to GIF.

### Install asciinema
```bash
# Python/pip
pip install asciinema

# Or system package manager
# Ubuntu/Debian:
sudo apt install asciinema

# macOS:
brew install asciinema
```

### Install agg (for GIF conversion)

agg requires Rust/Cargo:

```bash
# Install Rust if needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install agg
cargo install --git https://github.com/asciinema/agg
```

### Record and Convert
```bash
# Record
cd /home/jjshanks/workspace/racgoat
asciinema rec demo/racgoat-demo.cast
# ... use the app ...
# Press Ctrl+D when done

# Convert to GIF
agg demo/racgoat-demo.cast demo/racgoat-demo.gif
```

---

## Option 3: Simple Screen Recording

Use your OS's built-in screen recorder:

### macOS
1. Open QuickTime Player
2. File → New Screen Recording
3. Select terminal window
4. Record your demo
5. Export as video

### Linux (with ffmpeg)
```bash
# Install ffmpeg
sudo apt install ffmpeg  # Ubuntu/Debian

# Record (Ctrl+C to stop)
ffmpeg -video_size 1920x1080 -framerate 25 -f x11grab -i :0.0 demo/racgoat-demo.mp4
```

### Windows (WSL)
Use Windows Game Bar (Win+G) to record terminal window.

---

## Quick Start (No Installation)

If you can't install tools right now:

1. **Take screenshots** instead:
   - Use your OS screenshot tool
   - Capture 4-5 key screens
   - Annotate with arrows/text if needed

2. **Or use the built-in demo script**:
   ```bash
   ./demo/run_demo.sh
   # Choose option 3 for manual test
   ```

3. **Record a quick video with phone**:
   - Point at screen
   - Narrate what you're doing
   - Upload to YouTube/Vimeo

---

## Recommended: VHS

If starting fresh, install VHS. It's the easiest and creates the best results:

```bash
# macOS
brew install vhs

# Then run
cd /home/jjshanks/workspace/racgoat
vhs demo/demo.tape
```

Done! Your GIF will be at `demo/racgoat-demo.gif`.
