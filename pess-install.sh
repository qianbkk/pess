#!/bin/bash
# pess-install.sh — PESS 安装 shim (v3.8.0)
#
# 权威源已迁移到 pess.py (Python), 本脚本为向后兼容薄包装.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 调用 Python 统一入口
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "Error: python or python3 required" >&2
    exit 3
fi

$PY "$SCRIPT_DIR/pess.py" install

echo ""
echo "✅ PESS 安装完成 (via pess.py 权威源)"
echo "如需自定义: python pess.py install --help"
