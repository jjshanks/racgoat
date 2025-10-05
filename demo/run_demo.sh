#!/bin/bash
# RacGoat Demo Runner
# Helps create demo GIF/video for contest submission

set -e

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$DEMO_DIR")"

echo "🦝🐐 RacGoat Demo Generator"
echo "=========================="
echo ""

# Check for VHS
if command -v vhs &> /dev/null; then
    echo "✓ VHS found"
    USE_VHS=true
else
    echo "✗ VHS not found"
    echo "  Install: go install github.com/charmbracelet/vhs@latest"
    echo "  Or: brew install vhs"
    USE_VHS=false
fi

# Check for asciinema
if command -v asciinema &> /dev/null; then
    echo "✓ asciinema found"
    USE_ASCIINEMA=true
else
    echo "✗ asciinema not found"
    echo "  Install: pip install asciinema"
    USE_ASCIINEMA=false
fi

echo ""
echo "Choose demo method:"
echo "1) VHS (automated, creates GIF) - recommended"
echo "2) asciinema (record yourself, more natural)"
echo "3) Manual test (just run racgoat with sample diff)"
echo ""
read -p "Choice [1-3]: " choice

case $choice in
    1)
        if [ "$USE_VHS" = false ]; then
            echo "ERROR: VHS not installed. Install it first."
            exit 1
        fi
        echo ""
        echo "🎬 Running VHS demo..."
        cd "$PROJECT_DIR"
        vhs demo/demo.tape
        echo ""
        echo "✅ Demo GIF created: demo/racgoat-demo.gif"
        echo ""
        echo "Next steps:"
        echo "1. Review the GIF"
        echo "2. If needed, edit demo/demo.tape and re-run"
        echo "3. Add to README.md and contest submission"
        ;;
    2)
        if [ "$USE_ASCIINEMA" = false ]; then
            echo "ERROR: asciinema not installed. Install it first."
            exit 1
        fi
        echo ""
        echo "🎬 Starting asciinema recording..."
        echo ""
        echo "Instructions:"
        echo "1. The recording will start in 3 seconds"
        echo "2. Run: cat demo/sample.diff | uv run python -m racgoat -o demo/review.md"
        echo "3. Navigate, add comments, use search, show help"
        echo "4. Press 'q' to quit"
        echo "5. Show output: cat demo/review.md"
        echo "6. Press Ctrl+D to stop recording"
        echo ""
        read -p "Press Enter to start recording..."
        cd "$PROJECT_DIR"
        asciinema rec demo/racgoat-demo.cast
        echo ""
        echo "✅ Recording saved: demo/racgoat-demo.cast"
        echo ""
        echo "To convert to GIF:"
        echo "1. Install agg: cargo install agg"
        echo "2. Run: agg demo/racgoat-demo.cast demo/racgoat-demo.gif"
        ;;
    3)
        echo ""
        echo "🦝 Running manual test..."
        echo ""
        cd "$PROJECT_DIR"
        cat demo/sample.diff | uv run python -m racgoat -o demo/review.md
        echo ""
        echo "Review saved to: demo/review.md"
        echo ""
        read -p "Show review? [y/n]: " show
        if [ "$show" = "y" ]; then
            cat demo/review.md
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Done!"
