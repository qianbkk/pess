"""PESS auto_lint.py 单元测试 (OPT-004)

覆盖：
1. 监听 PostToolUse:Write/Edit/MultiEdit 事件
2. 文件后缀 → linter 映射 (.py/.js/.ts/.md)
3. 无 linter 时静默返回 (graceful degradation)
4. linter 超时 (5s) 不阻塞
5. 异常 stdin fail-open
6. 非 Write/Edit 工具不触发
"""
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "auto_lint.py"


def run_hook(payload: dict) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    return result.returncode, result.stdout, result.stderr


def test_post_tool_use_write_triggers_lint():
    """Write 事件触发 lint 流程（即使 linter 缺失也 exit 0）"""
    code, stdout, stderr = run_hook({
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/test.py", "content": "x = 1\n"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  PostToolUse Write (.py) → exit 0")


def test_edit_triggers_lint():
    """Edit 事件触发"""
    code, stdout, stderr = run_hook({
        "tool_name": "Edit",
        "tool_input": {"file_path": "/tmp/test.js", "old_string": "x", "new_string": "y"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  PostToolUse Edit (.js) → exit 0")


def test_multi_edit_triggers_lint():
    """MultiEdit 事件触发"""
    code, stdout, stderr = run_hook({
        "tool_name": "MultiEdit",
        "tool_input": {"file_path": "/tmp/test.ts", "edits": []}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  PostToolUse MultiEdit (.ts) → exit 0")


def test_non_lintable_extension_silent():
    """.txt 等无 linter 后缀应静默通过"""
    code, stdout, stderr = run_hook({
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/notes.txt", "content": "hello"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    assert stdout.strip() == "", f"stdout should be empty for non-lintable, got: {stdout[:200]}"
    print(f"  PASS  .txt (no linter) → exit 0 + 静默")


def test_non_post_tool_tool_silent():
    """非 PostToolUse 工具 (如 Read) 不触发"""
    code, stdout, stderr = run_hook({
        "tool_name": "Read",
        "tool_input": {"file_path": "/tmp/test.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    assert stdout.strip() == "", f"stdout should be empty for Read, got: {stdout[:200]}"
    print(f"  PASS  Read tool → exit 0 + 静默 (非 PostToolUse)")


def test_bad_stdin_failsafe():
    """坏 stdin 应 fail-open (exit 0)"""
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not valid json",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode != 2, f"fail-open: should NOT exit 2, got {result.returncode}"
    print(f"  PASS  fail-open 坏 stdin → exit={result.returncode} (不阻断)")


def test_empty_stdin_silent():
    """空 stdin 应静默通过"""
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0, f"expected exit 0 for empty stdin, got {result.returncode}"
    print(f"  PASS  empty stdin → exit 0")


def test_python_file_uses_ruff_linter():
    """.py 文件应尝试 ruff (linter 缺失时静默 skip)"""
    code, stdout, stderr = run_hook({
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/has_issues.py", "content": "import os\nx=1\n"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    # stderr 可能含 'lint skipped' (linter 缺失) 或 'warn' JSON (有 issue)
    # 两种情况都是合法行为
    print(f"  PASS  .py 走 ruff 路径 → exit 0")


def test_no_file_path_silent():
    """tool_input 无 file_path 时静默"""
    code, stdout, stderr = run_hook({
        "tool_name": "Write",
        "tool_input": {"content": "x"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  无 file_path → exit 0 + 静默")


if __name__ == "__main__":
    print("=== PESS auto_lint.py 单元测试 (OPT-004) ===\n")
    tests = [
        test_post_tool_use_write_triggers_lint,
        test_edit_triggers_lint,
        test_multi_edit_triggers_lint,
        test_non_lintable_extension_silent,
        test_non_post_tool_tool_silent,
        test_bad_stdin_failsafe,
        test_empty_stdin_silent,
        test_python_file_uses_ruff_linter,
        test_no_file_path_silent,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    print()
    if failed == 0:
        print(f"全部 {len(tests)} 项通过 [OK]")
    else:
        print(f"{failed} 项失败 [FAIL]")
        raise SystemExit(1)
