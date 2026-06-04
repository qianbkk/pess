"""PESS inject_context.py 单元测试 (OPT-005)

覆盖：
1. SessionStart 事件触发 memory-bank 注入
2. activeContext.md + progress.md 内容被读取
3. 注入大小限制 (PESS_INJECT_MAX_CHARS)
4. 无 memory-bank 目录时静默
5. 异常 stdin fail-open
6. 非 SessionStart 事件不触发
7. 部分文件缺失时仍能注入存在的文件
"""
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

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "inject_context.py"


def run_hook(payload: dict, cwd: str = None) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


def test_sessionstart_injects_memory_bank():
    """SessionStart + 有 memory-bank 时应输出 additionalContext JSON"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "test-proj"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "activeContext.md").write_text(
            "# Current Task\nImplementing feature X\n", encoding="utf-8"
        )
        (proj / "memory-bank" / "progress.md").write_text(
            "# Progress\n- [x] Step 1\n- [ ] Step 2\n", encoding="utf-8"
        )
        code, stdout, stderr = run_hook(
            {"hook_event_name": "SessionStart", "cwd": str(proj)},
            cwd=str(proj),
        )
        assert code == 0, f"expected exit 0, got {code}"
        out = json.loads(stdout.strip())
        assert "hookSpecificOutput" in out
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "activeContext.md" in ctx, f"activeContext.md not injected: {ctx[:200]}"
        assert "progress.md" in ctx, f"progress.md not injected: {ctx[:200]}"
        assert "Current Task" in ctx
        assert "Step 1" in ctx
    print(f"  PASS  SessionStart + memory-bank → 注入 activeContext+progress")


def test_no_memory_bank_silent():
    """无 memory-bank 目录时静默通过"""
    with tempfile.TemporaryDirectory() as tmp:
        code, stdout, stderr = run_hook(
            {"hook_event_name": "SessionStart"},
            cwd=tmp,
        )
        assert code == 0, f"expected exit 0, got {code}"
        assert stdout.strip() == "", f"stdout should be empty when no memory-bank, got: {stdout[:200]}"
    print(f"  PASS  无 memory-bank 目录 → exit 0 + 静默")


def test_non_sessionstart_event_silent():
    """非 SessionStart 事件不触发注入"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "activeContext.md").write_text("x", encoding="utf-8")
        code, stdout, stderr = run_hook(
            {"hook_event_name": "UserPromptSubmit"},
            cwd=str(proj),
        )
        assert code == 0, f"expected exit 0, got {code}"
        assert stdout.strip() == "", f"stdout should be empty for non-SessionStart, got: {stdout[:200]}"
    print(f"  PASS  UserPromptSubmit → exit 0 + 静默 (非 SessionStart)")


def test_partial_memory_bank_files():
    """部分 memory-bank 文件缺失时仍注入存在的文件"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "activeContext.md").write_text("X is the task", encoding="utf-8")
        # progress.md 不存在
        code, stdout, stderr = run_hook(
            {"hook_event_name": "SessionStart"},
            cwd=str(proj),
        )
        assert code == 0, f"expected exit 0, got {code}"
        out = json.loads(stdout.strip())
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "activeContext.md" in ctx
        assert "X is the task" in ctx
    print(f"  PASS  部分文件缺失 → 注入存在的文件")


def test_empty_memory_bank_silent():
    """memory-bank 存在但全部文件为空时静默"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "activeContext.md").write_text("", encoding="utf-8")
        code, stdout, stderr = run_hook(
            {"hook_event_name": "SessionStart"},
            cwd=str(proj),
        )
        assert code == 0, f"expected exit 0, got {code}"
        assert stdout.strip() == "", f"stdout should be empty for empty memory-bank, got: {stdout[:200]}"
    print(f"  PASS  memory-bank 全空 → exit 0 + 静默")


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
    assert result.returncode == 0, f"fail-open: should exit 0, got {result.returncode}"
    print(f"  PASS  fail-open 坏 stdin → exit 0")


def test_max_chars_truncation():
    """超大 memory-bank 内容应被截断到 PESS_INJECT_MAX_CHARS"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        # 写入 100KB 内容
        big_content = "x" * 100000
        (proj / "memory-bank" / "activeContext.md").write_text(big_content, encoding="utf-8")

        env_input = json.dumps({"hook_event_name": "SessionStart"})
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=env_input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            cwd=str(proj),
            env={"PATH": __import__("os").environ.get("PATH", ""),
                 "PYTHONIOENCODING": "utf-8",
                 "PESS_INJECT_MAX_CHARS": "1000"},
        )
        assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
        out = json.loads(result.stdout.strip())
        ctx = out["hookSpecificOutput"]["additionalContext"]
        # 截断后字符数 ≤ 1000 + "[truncated at..." 标签
        assert "truncated" in ctx, f"expected truncation marker, got: {ctx[:200]}"
        assert len(ctx) < 5000, f"context too long ({len(ctx)}), truncation failed"
    print(f"  PASS  100KB memory-bank → 截断到 PESS_INJECT_MAX_CHARS=1000")


def test_injects_multiple_files_in_order():
    """多个 memory-bank 文件应按 INJECT_FILES 顺序拼接"""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "p"
        (proj / "memory-bank").mkdir(parents=True)
        (proj / "memory-bank" / "activeContext.md").write_text("AAA_activeContext", encoding="utf-8")
        (proj / "memory-bank" / "progress.md").write_text("BBB_progress", encoding="utf-8")
        (proj / "memory-bank" / "constitution.md").write_text("CCC_constitution", encoding="utf-8")

        code, stdout, stderr = run_hook(
            {"hook_event_name": "SessionStart"},
            cwd=str(proj),
        )
        assert code == 0, f"expected exit 0, got {code}"
        ctx = json.loads(stdout.strip())["hookSpecificOutput"]["additionalContext"]
        # activeContext 应在 progress 之前, progress 在 constitution 之前
        a_pos = ctx.find("AAA_activeContext")
        b_pos = ctx.find("BBB_progress")
        c_pos = ctx.find("CCC_constitution")
        assert 0 < a_pos < b_pos < c_pos, f"order wrong: a={a_pos} b={b_pos} c={c_pos}"
    print(f"  PASS  多文件按 INJECT_FILES 顺序拼接")


if __name__ == "__main__":
    print("=== PESS inject_context.py 单元测试 (OPT-005) ===\n")
    tests = [
        test_sessionstart_injects_memory_bank,
        test_no_memory_bank_silent,
        test_non_sessionstart_event_silent,
        test_partial_memory_bank_files,
        test_empty_memory_bank_silent,
        test_bad_stdin_failsafe,
        test_max_chars_truncation,
        test_injects_multiple_files_in_order,
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
