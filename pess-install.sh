#!/bin/bash
# pess-install.sh — Install PESS global components (run once, macOS/Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
PESS_ROOT="$SCRIPT_DIR"

echo "Installing PESS global components..."

# 1. Create directories
mkdir -p "$HOOKS_DIR"

# 2. Copy hooks
cp "$PESS_ROOT/hooks/guard_files.py" "$HOOKS_DIR/"
cp "$PESS_ROOT/hooks/guard_commands.py" "$HOOKS_DIR/"
echo "Hooks installed to $HOOKS_DIR"

# 3. Write settings.json
SETTINGS_PATH="$CLAUDE_DIR/settings.json"
NEW_HOOKS_JSON='{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"'"$HOOKS_DIR"'/guard_files.py\""
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"'"$HOOKS_DIR"'/guard_commands.py\""
          }
        ]
      }
    ]
  }
}'

if [ -f "$SETTINGS_PATH" ]; then
    echo "Warning: $SETTINGS_PATH already exists. Please merge hooks manually:"
    echo "$NEW_HOOKS_JSON"
else
    echo "$NEW_HOOKS_JSON" > "$SETTINGS_PATH"
    echo "settings.json written"
fi

# 4. Copy global CLAUDE.md
GLOBAL_CLAUDE="$CLAUDE_DIR/CLAUDE.md"
if [ ! -f "$GLOBAL_CLAUDE" ]; then
    cp "$PESS_ROOT/templates/global-CLAUDE.md" "$GLOBAL_CLAUDE"
    echo "Global CLAUDE.md installed"
else
    echo "Global CLAUDE.md already exists, skipping"
fi

echo ""
echo "PESS installation complete."