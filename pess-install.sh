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

# 2.5 验证 Python 可用性 (OPT-003 配套, 跨平台一致性)
PYTHON_OK=0
for cmd in python python3 py; do
    ver=$($cmd --version 2>&1 || true)
    if echo "$ver" | grep -qE "^Python 3\.[89]|^Python 3\.1[0-9]|^Python 3\.1[2-9]"; then
        echo "Python detected: $ver"
        PYTHON_OK=1
        break
    fi
done
if [ "$PYTHON_OK" -eq 0 ]; then
    echo "Warning: Python 3.8+ not detected. Hooks installed but may not run; install Python 3.8+ and ensure it is in PATH." >&2
fi

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