"""PESS enforce_constitution.py 单元测试 (OPT-028)"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "enforce_constitution.py"


def run_hook(payload: dict, cwd: str = None) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


def test_userpromptsubmit_injects_constitution():
    """UserPromptSubmit + 有 constitution.md 时应注入"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "constitution.md").write_text(
            "## Quality底线\n- Coverage: service >= 85%\n- No bare except\n",
            encoding="utf-8",
        )
        code, stdout, stderr = run_hook(
            {"hook_event_name": "UserPromptSubmit", "cwd": str(proj)},
            cwd=str(proj),
        )
        assert code == 0
        out = json.loads(stdout.strip())
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "Constitution" in ctx
        assert "Quality底线" in ctx
    print(f"  PASS  UserPromptSubmit + constitution → 注入宪法")


def test_no_constitution_silent():
    """无 constitution.md 时静默"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        code, stdout, stderr = run_hook(
            {"hook_event_name": "UserPromptSubmit"},
            cwd=str(proj),
        )
        assert code == 0
        assert stdout.strip() == ""
    print(f"  PASS  无 constitution.md → exit 0 + 静默")


def test_non_userpromptsubmit_silent():
    """非 UserPromptSubmit 事件不触发"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "constitution.md").write_text("X", encoding="utf-8")
        code, stdout, stderr = run_hook(
            {"hook_event_name": "PreToolUse"},
            cwd=str(proj),
        )
        assert code == 0
        assert stdout.strip() == ""
    print(f"  PASS  PreToolUse → 静默 (非 UserPromptSubmit)")


def test_bad_stdin_failsafe():
    """坏 stdin 应 fail-open"""
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="bad json",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    print(f"  PASS  fail-open 坏 stdin → exit 0")


def test_truncation_2kb():
    """超大 constitution 应截断到 2KB"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "constitution.md").write_text("X" * 10000, encoding="utf-8")
        code, stdout, stderr = run_hook(
            {"hook_event_name": "UserPromptSubmit"},
            cwd=str(proj),
        )
        assert code == 0
        ctx = json.loads(stdout.strip())["hookSpecificOutput"]["additionalContext"]
        assert "truncated" in ctx
        assert len(ctx) < 5000
    print(f"  PASS  10KB constitution → 截断到 2KB")


if __name__ == "__main__":
    print("=== PESS enforce_constitution.py 单元测试 (OPT-028) ===\n")
    tests = [
        test_userpromptsubmit_injects_constitution,
        test_no_constitution_silent,
        test_non_userpromptsubmit_silent,
        test_bad_stdin_failsafe,
        test_truncation_2kb,
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
