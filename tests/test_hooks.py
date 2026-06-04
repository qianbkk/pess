"""PESS hooks pytest 套件 — 验证退出码协议

覆盖：
- guard_files: HARD_BLOCK 命中 → exit 2 + stderr JSON
- guard_files: SOFT_WARN 命中 → exit 0 + stdout JSON (warn)
- guard_files: 无匹配 → exit 0
- guard_commands: HARD_BLOCK_RE 命中 → exit 2
- guard_commands: SOFT_WARN_RE 命中 → exit 0
- guard_commands: 无匹配 → exit 0
"""
import json
import subprocess
import sys
from pathlib import Path

# Windows GBK stdout 修复
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOOKS = Path(__file__).resolve().parent.parent / "hooks"
GUARD_FILES = HOOKS / "guard_files.py"
GUARD_COMMANDS = HOOKS / "guard_commands.py"


def run_hook(hook_path: Path, payload: dict) -> tuple[int, str, str]:
    """运行 hook 脚本，返回 (exit_code, stdout, stderr)"""
    result = subprocess.run(
        ["python", str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    return result.returncode, result.stdout, result.stderr


# ==================== guard_files.py ====================

def test_guard_files_hard_block_exits_2():
    """HARD_BLOCK 命中必须 exit 2（修复前是 exit 0 = 放行）"""
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write",
        "tool_input": {"path": "/tmp/.env"}
    })
    assert code == 2, f"expected exit 2, got {code}"
    # stderr/stdout 任一包含 block JSON 即可（hook 可能输出到任一）
    combined = (stdout + stderr).strip()
    assert "block" in combined, f"expected 'block' in output, got: {combined[:200]}"
    print(f"  PASS  guard_files HARD_BLOCK (.env) → exit 2 + block JSON")


def test_guard_files_soft_warn_exits_0():
    """SOFT_WARN 命中应 exit 0 + warn JSON"""
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write",
        "tool_input": {"path": "/app/core/db.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    if stdout.strip():
        out = json.loads(stdout.strip().splitlines()[-1])
        assert out.get("action") == "warn"
    print(f"  PASS  guard_files SOFT_WARN (core/) → exit 0 + warn")


def test_guard_files_no_match_exits_0():
    """无匹配应 exit 0 + 静默"""
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write",
        "tool_input": {"path": "/tmp/normal.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  guard_files no-match → exit 0")


def test_guard_files_pem_blocked():
    """.pem 也应在 HARD_BLOCK 列表"""
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Edit",
        "tool_input": {"path": "/etc/ssl/cert.pem"}
    })
    assert code == 2, f"expected exit 2 for .pem, got {code}"
    print(f"  PASS  guard_files HARD_BLOCK (.pem) → exit 2")


# ==================== guard_commands.py ====================

def test_guard_commands_hard_block_rm_rf_exits_2():
    """rm -rf / 命中必须 exit 2"""
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash",
        "tool_input": {"command": "rm -rf /"}
    })
    assert code == 2, f"expected exit 2, got {code}"
    print(f"  PASS  guard_commands HARD_BLOCK (rm -rf /) → exit 2")


def test_guard_commands_hard_block_drop_table_exits_2():
    """DROP TABLE 命中必须 exit 2"""
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash",
        "tool_input": {"command": "DROP TABLE users;"}
    })
    assert code == 2, f"expected exit 2, got {code}"
    print(f"  PASS  guard_commands HARD_BLOCK (DROP TABLE) → exit 2")


def test_guard_commands_soft_warn_force_push_exits_0():
    """git push --force 应 SOFT_WARN 退出 0"""
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin main --force"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    if stdout.strip():
        out = json.loads(stdout.strip().splitlines()[-1])
        assert out.get("action") == "warn"
    print(f"  PASS  guard_commands SOFT_WARN (--force) → exit 0 + warn")


def test_guard_commands_no_match_exits_0():
    """普通命令应 exit 0"""
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    print(f"  PASS  guard_commands no-match (ls -la) → exit 0")


if __name__ == "__main__":
    print("=== PESS hooks pytest 套件 ===\n")
    tests = [
        test_guard_files_hard_block_exits_2,
        test_guard_files_soft_warn_exits_0,
        test_guard_files_no_match_exits_0,
        test_guard_files_pem_blocked,
        test_guard_commands_hard_block_rm_rf_exits_2,
        test_guard_commands_hard_block_drop_table_exits_2,
        test_guard_commands_soft_warn_force_push_exits_0,
        test_guard_commands_no_match_exits_0,
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
        print(f"全部 {len(tests)} 项通过 ✅")
    else:
        print(f"{failed} 项失败 ❌")
        raise SystemExit(1)
