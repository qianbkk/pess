"""PESS hooks pytest 套件 — 验证退出码协议 + 全部 17 条规则

覆盖矩阵：
- guard_files: 6 HARD_BLOCK + 4 SOFT_WARN = 10 项
- guard_commands: 3 HARD_BLOCK_RE + 4 SOFT_WARN_RE = 7 项
- 无匹配边界 = 2 项
- 退出码合规 + stderr 方向 = 多处断言
- 总计 19 项 Assert
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
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    return result.returncode, result.stdout, result.stderr


# ==================== guard_files.py 退出码协议 ====================

def _assert_block(code, stdout, stderr, label):
    """通用断言：HARD_BLOCK 必须 exit 2 + stderr 含 block JSON + stdout 空"""
    assert code == 2, f"{label}: expected exit 2, got {code}"
    assert "block" in stderr, f"{label}: expected 'block' in stderr, got: {stderr[:200]}"
    assert stdout.strip() == "", f"{label}: stdout should be empty, got: {stdout[:200]}"


def _assert_warn(code, stdout, stderr, label):
    """通用断言：SOFT_WARN 必须 exit 0 + stdout 含 warn JSON"""
    assert code == 0, f"{label}: expected exit 0, got {code}"
    assert "warn" in stdout, f"{label}: expected 'warn' in stdout, got: {stdout[:200]}"


def _assert_pass(code, stdout, stderr, label):
    """通用断言：无匹配必须 exit 0 + 静默"""
    assert code == 0, f"{label}: expected exit 0, got {code}"
    assert stdout.strip() == "", f"{label}: stdout should be empty, got: {stdout[:200]}"
    assert stderr.strip() == "", f"{label}: stderr should be empty, got: {stderr[:200]}"


# ==================== guard_files.py — 6 条 HARD_BLOCK 全覆盖 ====================

def test_guard_files_block_env():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/tmp/.env"}
    })
    _assert_block(code, stdout, stderr, ".env")
    print(f"  PASS  guard_files HARD_BLOCK [.env]  exit 2 + stderr block")


def test_guard_files_block_pem():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Edit", "tool_input": {"path": "/etc/ssl/cert.pem"}
    })
    _assert_block(code, stdout, stderr, ".pem")
    print(f"  PASS  guard_files HARD_BLOCK [.pem]  exit 2 + stderr block")


def test_guard_files_block_key():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/home/user/private.key"}
    })
    _assert_block(code, stdout, stderr, ".key")
    print(f"  PASS  guard_files HARD_BLOCK [.key]  exit 2 + stderr block")


def test_guard_files_block_pfx():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/certs/server.pfx"}
    })
    _assert_block(code, stdout, stderr, ".pfx")
    print(f"  PASS  guard_files HARD_BLOCK [.pfx]  exit 2 + stderr block")


def test_guard_files_block_secrets_yaml():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/config/secrets.yaml"}
    })
    _assert_block(code, stdout, stderr, "secrets.yaml")
    print(f"  PASS  guard_files HARD_BLOCK [secrets.yaml]  exit 2 + stderr block")


def test_guard_files_block_secrets_json():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/config/secrets.json"}
    })
    _assert_block(code, stdout, stderr, "secrets.json")
    print(f"  PASS  guard_files HARD_BLOCK [secrets.json]  exit 2 + stderr block")


# ==================== guard_files.py — 4 条 SOFT_WARN 全覆盖 ====================

def test_guard_files_warn_core():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/core/db.py"}
    })
    # v3.8.0: SOFT_WARN 改走 stderr (与 auto_lint.py 一致)
    assert code == 0, f"expected exit 0, got {code}"
    assert "warn" in stderr, f"expected 'warn' in stderr, got: {stderr[:200]}"
    print(f"  PASS  guard_files SOFT_WARN [/core/]  exit 0 + stderr warn")


def test_guard_files_warn_migrations():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/migrations/v1.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    assert "warn" in stderr, f"expected 'warn' in stderr, got: {stderr[:200]}"
    print(f"  PASS  guard_files SOFT_WARN [/migrations/]  exit 0 + stderr warn")


def test_guard_files_warn_settings():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/proj/settings.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    assert "warn" in stderr, f"expected 'warn' in stderr, got: {stderr[:200]}"
    print(f"  PASS  guard_files SOFT_WARN [settings.py]  exit 0 + stderr warn")


def test_guard_files_warn_config():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/app/proj/config.py"}
    })
    assert code == 0, f"expected exit 0, got {code}"
    assert "warn" in stderr, f"expected 'warn' in stderr, got: {stderr[:200]}"
    print(f"  PASS  guard_files SOFT_WARN [config.py]  exit 0 + stderr warn")


# ==================== guard_files.py — 无匹配边界 ====================

def test_guard_files_no_match():
    code, stdout, stderr = run_hook(GUARD_FILES, {
        "tool_name": "Write", "tool_input": {"path": "/tmp/normal.py"}
    })
    _assert_pass(code, stdout, stderr, "no match")
    print(f"  PASS  guard_files no-match  exit 0 + 静默")


# ==================== guard_commands.py — 3 条 HARD_BLOCK_RE 全覆盖 ====================

def test_guard_commands_block_rm_rf_root():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "rm -rf /"}
    })
    _assert_block(code, stdout, stderr, "rm -rf /")
    print(f"  PASS  guard_commands HARD_BLOCK [rm -rf /]  exit 2 + stderr block")


def test_guard_commands_block_drop_table():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "DROP TABLE users;"}
    })
    _assert_block(code, stdout, stderr, "DROP TABLE")
    print(f"  PASS  guard_commands HARD_BLOCK [DROP TABLE]  exit 2 + stderr block")


def test_guard_commands_block_disk_write():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "echo x > /dev/sda"}
    })
    _assert_block(code, stdout, stderr, ">/dev/sda")
    print(f"  PASS  guard_commands HARD_BLOCK [>/dev/sda]  exit 2 + stderr block")


# ==================== guard_commands.py — 4 条 SOFT_WARN_RE 全覆盖 ====================

def test_guard_commands_warn_force_push():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "git push origin main --force"}
    })
    _assert_warn(code, stdout, stderr, "--force")
    print(f"  PASS  guard_commands SOFT_WARN [--force]  exit 0 + warn")


def test_guard_commands_warn_npm_publish():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "npm publish"}
    })
    _assert_warn(code, stdout, stderr, "npm publish")
    print(f"  PASS  guard_commands SOFT_WARN [npm publish]  exit 0 + warn")


def test_guard_commands_warn_pip_break():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "pip install requests --break-system"}
    })
    _assert_warn(code, stdout, stderr, "pip --break-system")
    print(f"  PASS  guard_commands SOFT_WARN [pip --break-system]  exit 0 + warn")


def test_guard_commands_warn_kubectl_delete():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "kubectl delete pod nginx"}
    })
    _assert_warn(code, stdout, stderr, "kubectl delete")
    print(f"  PASS  guard_commands SOFT_WARN [kubectl delete]  exit 0 + warn")


# ==================== guard_commands.py — 无匹配边界 ====================

def test_guard_commands_no_match():
    code, stdout, stderr = run_hook(GUARD_COMMANDS, {
        "tool_name": "Bash", "tool_input": {"command": "ls -la"}
    })
    _assert_pass(code, stdout, stderr, "no match")
    print(f"  PASS  guard_commands no-match  exit 0 + 静默")


# ==================== 异常处理边界 ====================

def test_guard_files_bad_stdin_failsafe():
    """坏 stdin 应该 fail-open（exit 0 = 放行），不阻断用户

    设计：hook 故障时不应阻断用户是安全正确行为
    """
    result = subprocess.run(
        [sys.executable, str(GUARD_FILES)],
        input="not valid json {{{",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    # fail-open: 非 0 也行（异常栈），但不能是 2（阻断）
    assert result.returncode != 2, f"fail-open: should NOT exit 2 on bad stdin, got {result.returncode}"
    print(f"  PASS  guard_files fail-open 坏 stdin 不阻断 (exit={result.returncode})")


if __name__ == "__main__":
    print("=== PESS hooks pytest 套件 (19 项) ===\n")
    tests = [
        # guard_files HARD_BLOCK (6)
        test_guard_files_block_env,
        test_guard_files_block_pem,
        test_guard_files_block_key,
        test_guard_files_block_pfx,
        test_guard_files_block_secrets_yaml,
        test_guard_files_block_secrets_json,
        # guard_files SOFT_WARN (4)
        test_guard_files_warn_core,
        test_guard_files_warn_migrations,
        test_guard_files_warn_settings,
        test_guard_files_warn_config,
        # guard_files no-match (1)
        test_guard_files_no_match,
        # guard_commands HARD_BLOCK (3)
        test_guard_commands_block_rm_rf_root,
        test_guard_commands_block_drop_table,
        test_guard_commands_block_disk_write,
        # guard_commands SOFT_WARN (4)
        test_guard_commands_warn_force_push,
        test_guard_commands_warn_npm_publish,
        test_guard_commands_warn_pip_break,
        test_guard_commands_warn_kubectl_delete,
        # guard_commands no-match (1)
        test_guard_commands_no_match,
        # fail-safe (1)
        test_guard_files_bad_stdin_failsafe,
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
