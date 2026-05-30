#!/bin/bash
# pess-update.sh — Update PESS to latest version (macOS/Linux)
# Usage: bash pess-update.sh [--check]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CURRENT_VERSION="3.2.0"
UPDATE_BASE="https://github.com/qianbkk/pess.git"

usage() {
    echo "Usage: $0 [--check]"
    echo "  --check  Only check for updates, do not install"
    exit 0
}

CHECK_ONLY=false
if [ "$1" = "--check" ]; then
    CHECK_ONLY=true
fi

echo "PESS Updater v$CURRENT_VERSION"

if [ "$CHECK_ONLY" = true ]; then
    echo "Checking for updates..."
    LATEST_TAG=$(git -C "$SCRIPT_DIR" describe --tags 2>/dev/null | sed 's/v//' || echo "$CURRENT_VERSION")
    if [ "$LATEST_TAG" = "$CURRENT_VERSION" ]; then
        echo "You are on the latest version: v$CURRENT_VERSION"
    else
        echo "New version available: v$LATEST_TAG (you have v$CURRENT_VERSION)"
    fi
    exit 0
fi

echo "Fetching latest version from GitHub..."

# Preserve existing user hooks
LOCAL_HOOKS=""
if [ -d "$HOME/.claude/hooks" ]; then
    LOCAL_HOOKS="$HOME/.claude/hooks"
    echo "Preserving existing hooks in $LOCAL_HOOKS"
fi

# Add upstream remote and fetch
git remote add pess-upstream "$UPDATE_BASE" 2>/dev/null || \
    git remote set-url pess-upstream "$UPDATE_BASE"

echo "Pulling PESS updates..."
git fetch pess-upstream main --tags

# Update templates and scripts (never overwrite user customizations)
echo "Updating templates and scripts..."

for path in templates/ hooks/ pess-install.sh pess-init.sh pess-update.sh AGENTS.md CHANGELOG.md .gitignore; do
    git checkout "pess-upstream/main" -- "$path" 2>/dev/null || true
done

echo ""
echo "PESS has been updated to the latest version."
echo ""
echo "Files that were NOT overwritten (your customizations preserved):"
echo "  - CLAUDE.md"
echo "  - memory-bank/"
echo ""

LATEST_TAG=$(git -C "$SCRIPT_DIR" describe --tags --abbrev=0 2>/dev/null | sed 's/v//' || echo "$CURRENT_VERSION")
echo "Current version: v$CURRENT_VERSION"
echo "Latest version: v$LATEST_TAG"

if [ "$LATEST_TAG" != "$CURRENT_VERSION" ]; then
    echo "What's new:"
    git -C "$SCRIPT_DIR" log --oneline "v$CURRENT_VERSION".."v$LATEST_TAG" 2>/dev/null || true
fi