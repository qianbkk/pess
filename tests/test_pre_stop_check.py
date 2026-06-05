"""PESS pre_stop_check.py 单元测试 (OPT-023, v3.8.0 补)"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "pre_stop_check.py"


def run_hook(payload: dict, cwd: str = None, env: dict = None) -> tuple[int, str, str]:
    base_env = os.environ.copy()
    if env:
        base_env.update(env)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        cwd=cwd,
        env=base_env,
    )
    return result.returncode, result.stdout, result.stderr


def test_stop_silent_when_no_completion_signal():
    """无 '完成' 类信号 → 静默 (exit 0, 无警告)"""
    code, stdout, stderr = run_hook({
        "hook_event_name": "Stop",
        "last_assistant_message": "我正在思考这个问题的多种解法..."
    })
    assert code == 0
    assert "完成" not in stderr
    assert "skip" not in stderr.lower() and "warn" not in stderr.lower()
    print("  PASS  无完成信号 → exit 0 + 静默")


def test_stop_warn_soft_when_completion_no_recent_test():
    """'完成' 信号 + 5 分钟内未跑测试 → soft_warn (exit 0 + stderr)"""
    with tempfile.TemporaryDirectory() as tmp:
        # 确保无 .pytest_cache / .coverage
        code, stdout, stderr = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "功能已完成, 可以 merge 了"
        }, cwd=tmp)
        assert code == 0, f"soft_warn 应 exit 0, got {code}"
        # 警告应在 stderr
        assert "测试" in stderr or "test" in stderr.lower()
    print("  PASS  完成信号 + 未跑测试 → soft_warn (exit 0 + stderr)")


def test_stop_silent_when_recent_test_run():
    """完成信号 + 5 分钟内跑了测试 → 静默"""
    with tempfile.TemporaryDirectory() as tmp:
        # 模拟刚跑过测试 (mtime 在 60s 前)
        pytest_cache = Path(tmp) / ".pytest_cache"
        pytest_cache.mkdir()
        # mtime 设为 1 分钟前
        old_time = (datetime.now() - timedelta(minutes=1)).timestamp()
        os.utime(pytest_cache, (old_time, old_time))

        code, stdout, stderr = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "功能已完成, 测试全过"
        }, cwd=tmp)
        assert code == 0
        # 既然有 recent test, 应静默通过
        assert "stop soft_warn" not in stderr.lower()
    print("  PASS  完成信号 + 最近跑测试 → exit 0 + 静默")


def test_stop_hard_block_mode():
    """PESS_STOP_MODE=hard_block + 完成 + 未跑测试 → exit 2"""
    with tempfile.TemporaryDirectory() as tmp:
        code, stdout, stderr = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "I am done, ready to ship"
        }, cwd=tmp, env={"PESS_STOP_MODE": "hard_block"})
        assert code == 2, f"hard_block 应 exit 2, got {code}"
        assert "阻断" in stderr or "block" in stderr.lower()
    print("  PASS  hard_block 模式 → exit 2 + 阻断警告")


def test_non_stop_event_silent():
    """非 Stop 事件不触发"""
    code, stdout, stderr = run_hook({
        "hook_event_name": "PreToolUse",
        "last_assistant_message": "完成"
    })
    assert code == 0
    assert "warn" not in stderr.lower()
    print("  PASS  PreToolUse 事件 → 静默 (非 Stop)")


def test_bad_stdin_silent():
    """坏 stdin 应 fail-open"""
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    print("  PASS  fail-open 坏 stdin → exit 0")


if __name__ == "__main__":
    print("=== PESS pre_stop_check.py 单元测试 (OPT-023 v3.8.0) ===\n")
    tests = [
        test_stop_silent_when_no_completion_signal,
        test_stop_warn_soft_when_completion_no_recent_test,
        test_stop_silent_when_recent_test_run,
        test_stop_hard_block_mode,
        test_non_stop_event_silent,
        test_bad_stdin_silent,
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
