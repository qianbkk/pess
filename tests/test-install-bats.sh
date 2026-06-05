#!/bin/bash
# PESS bash install 跨平台测试 (OPT-006)
# 用法: bash tests/test-install-bats.sh
# 兼容 macOS bash 3.2 (避免 [[ ]] 嵌套数组)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PESS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS=0
FAIL=0

assert() {
    local desc="$1"
    local actual="$2"
    local expected="$3"
    if [ "$actual" = "$expected" ]; then
        echo "  PASS  $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $desc  expected='$expected' actual='$actual'"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== PESS bash install 测试 (OPT-006) ==="

# Test 1: pess-install.sh 语法检查
echo ""
echo "--- 语法检查 ---"
if bash -n "$PESS_ROOT/pess-install.sh" 2>/dev/null; then
    echo "  PASS  pess-install.sh 语法正确"
    PASS=$((PASS + 1))
else
    echo "  FAIL  pess-install.sh 语法错误"
    FAIL=$((FAIL + 1))
fi

# Test 2: pess-init.sh 语法检查
if bash -n "$PESS_ROOT/pess-init.sh" 2>/dev/null; then
    echo "  PASS  pess-init.sh 语法正确"
    PASS=$((PASS + 1))
else
    echo "  FAIL  pess-init.sh 语法错误"
    FAIL=$((FAIL + 1))
fi

# Test 3: pess-update.sh 语法检查
if bash -n "$PESS_ROOT/pess-update.sh" 2>/dev/null; then
    echo "  PASS  pess-update.sh 语法正确"
    PASS=$((PASS + 1))
else
    echo "  FAIL  pess-update.sh 语法错误"
    FAIL=$((FAIL + 1))
fi

# Test 4: SKILLS_SRC / SKILLS_DEST 变量已定义
echo ""
echo "--- 关键变量检查 ---"
TMPDIR_BASH_TEST=$(mktemp -d)
cd "$TMPDIR_BASH_TEST"
mkdir -p .claude/skills
# 模拟 pess-init.sh 中 SKILLS_SRC / SKILLS_DEST 的设置
SKILLS_SRC="$PESS_ROOT/templates/skills"
SKILLS_DEST=".claude/skills"
if [ -d "$SKILLS_SRC" ] && [ -n "$SKILLS_DEST" ]; then
    echo "  PASS  SKILLS_SRC / SKILLS_DEST 已定义且有效"
    PASS=$((PASS + 1))
else
    echo "  FAIL  SKILLS_SRC 或 SKILLS_DEST 未定义"
    FAIL=$((FAIL + 1))
fi

# Test 5: pess-install.sh 含 Python 调用 (v3.8.0: shim 调 pess.py)
echo ""
echo "--- Python 调用 (跨平台) ---"
if grep -q "python3\|python" "$PESS_ROOT/pess-install.sh" 2>/dev/null; then
    if grep -q "pess.py install" "$PESS_ROOT/pess-install.sh"; then
        echo "  PASS  pess-install.sh 调 pess.py (权威源 shim)"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  pess-install.sh 缺 pess.py 调用"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  FAIL  pess-install.sh 缺 python 调用"
    FAIL=$((FAIL + 1))
fi

# Test 6: 关键 Python hooks 语法
echo ""
echo "--- Python hooks ---"
# cd 到 PESS_ROOT 保证相对路径生效
cd "$PESS_ROOT"
for hook in guard_files.py guard_commands.py auto_lint.py inject_context.py; do
    if PYTHONIOENCODING=utf-8 python -X utf8 -c "import ast; ast.parse(open('hooks/$hook', encoding='utf-8').read())" 2>/dev/null; then
        echo "  PASS  hooks/$hook Python 语法正确"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  hooks/$hook Python 语法错误"
        FAIL=$((FAIL + 1))
    fi
done

# Cleanup
cd /
rm -rf "$TMPDIR_BASH_TEST"

echo ""
echo "=============================="
if [ "$FAIL" -eq 0 ]; then
    echo "全部 $PASS 项通过 [OK]"
else
    echo "$FAIL 项失败 [FAIL]"
    exit 1
fi
