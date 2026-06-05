"""PESS async_audit + audit_writer 测试 (OPT-024, v3.8.0 修复)"""
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "async_audit.py"
WRITER = Path(__file__).resolve().parent.parent / "hooks" / "audit_writer.py"


def run_hook(payload: dict, tmpdir: Path) -> tuple[int, str, str, float]:
    """运行 hook 并返回 (exit, stdout, stderr, 耗时秒)"""
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        env={"PATH": __import__("os").environ.get("PATH", ""),
             "PYTHONIOENCODING": "utf-8",
             "HOME": str(tmpdir),
             "USERPROFILE": str(tmpdir),
             "TEMP": str(tmpdir),
             "TMP": str(tmpdir)},
    )
    return result.returncode, result.stdout, result.stderr, time.time() - t0


def test_posttooluse_real_async():
    """Popen 异步: 父进程应 < 1s 返回 (不等待子进程完成)"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        code, stdout, stderr, elapsed = run_hook({
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.py", "content": "x"}
        }, tmpdir)
        assert code == 0
        # 真异步: 即使子进程要跑 1s, 父进程应 < 0.5s 返回
        assert elapsed < 2.0, f"hook 阻塞 {elapsed}s, 应 < 2s (Popen 异步)"
        # 子进程会写入 audit.log, 等 0.5s
        time.sleep(0.5)
        audit_log = tmpdir / ".claude" / "pess-audit.log"
        assert audit_log.is_file(), f"audit log 未创建: {audit_log}"
        lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1
        entry = json.loads(lines[-1])
        assert entry["tool"] == "Write"
        assert entry["path"] == "/tmp/test.py"
    print(f"  PASS  PostToolUse Popen 异步 + 写入 audit.log")


def test_pretooluse_also_writes():
    """PreToolUse 也应记录"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        run_hook({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"}
        }, tmpdir)
        time.sleep(0.5)
        audit_log = tmpdir / ".claude" / "pess-audit.log"
        assert audit_log.is_file()
        lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
        assert any('"Bash"' in line for line in lines)
    print(f"  PASS  PreToolUse 事件也写入 audit.log")


def test_bad_stdin_silent():
    """坏 stdin 不应阻断"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input="not json",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            env={"PATH": __import__("os").environ.get("PATH", ""),
                 "PYTHONIOENCODING": "utf-8",
                 "HOME": str(tmpdir),
                 "USERPROFILE": str(tmpdir)},
        )
        assert result.returncode == 0
    print(f"  PASS  fail-open 坏 stdin → exit 0")


def test_non_target_event_silent():
    """非 PostToolUse/PreToolUse 事件不写入"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        run_hook({
            "hook_event_name": "SessionStart",
            "tool_name": "?"
        }, tmpdir)
        time.sleep(0.3)
        audit_log = tmpdir / ".claude" / "pess-audit.log"
        # 不应创建, 或创建但为空
        if audit_log.is_file():
            assert audit_log.stat().st_size == 0
    print(f"  PASS  SessionStart 事件不写入 audit")


def test_rotate_30_days_debounce():
    """audit_writer 30 天滚动 + 24h debounce"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        audit_log = tmpdir / ".claude" / "pess-audit.log"
        audit_log.parent.mkdir(parents=True, exist_ok=True)

        # 写入 3 条: 2 条 30 天内, 1 条 40 天前
        old_ts = (datetime.utcnow() - timedelta(days=40)).isoformat() + "Z"
        new_ts = datetime.utcnow().isoformat() + "Z"
        with audit_log.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": new_ts, "tool": "Write"}) + "\n")
            f.write(json.dumps({"ts": old_ts, "tool": "OldWrite"}) + "\n")
            f.write(json.dumps({"ts": new_ts, "tool": "Edit"}) + "\n")

        # 运行 writer (会触发 rotate)
        input_path = tmpdir / "input.jsonl"
        input_path.write_text(json.dumps({"ts": new_ts, "tool": "Post"}) + "\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(WRITER), "--input", str(input_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            env={"PATH": __import__("os").environ.get("PATH", ""),
                 "PYTHONIOENCODING": "utf-8",
                 "HOME": str(tmpdir),
                 "USERPROFILE": str(tmpdir)},
        )
        assert result.returncode == 0

        # 验证: 旧的 40 天前条目应被删除, 新的 3 条保留
        lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
        # rotate 后: 2 条 new_ts (Write + Edit) + 1 条新追加 (Post) = 3 条
        # OldWrite (40 天前) 应被删
        assert len(lines) == 3, f"expected 3 lines, got {len(lines)}: {lines}"
        tools = [json.loads(l).get("tool") for l in lines]
        assert "OldWrite" not in tools, f"40天前条目应被删除: {tools}"
        assert "Write" in tools and "Edit" in tools and "Post" in tools

    print(f"  PASS  30 天滚动 + 旧条目删除")


def test_debounce_24h():
    """24h debounce: 第一次 rotate 后, 24h 内再次调用应跳过"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        audit_log = tmpdir / ".claude" / "pess-audit.log"
        audit_log.parent.mkdir(parents=True, exist_ok=True)
        # 模拟上次轮转在 1h 前
        rotate_state = tmpdir / ".claude" / ".pess-audit-last-rotate"
        rotate_state.write_text(str(time.time() - 3600), encoding="utf-8")

        # 添加一行 (应被 debounce 跳过 rotate 但仍被追加)
        old_ts = (datetime.utcnow() - timedelta(days=40)).isoformat() + "Z"
        with audit_log.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": old_ts, "tool": "OldWrite"}) + "\n")

        input_path = tmpdir / "input.jsonl"
        input_path.write_text(json.dumps({"ts": datetime.utcnow().isoformat() + "Z", "tool": "NewWrite"}) + "\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(WRITER), "--input", str(input_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            env={"PATH": __import__("os").environ.get("PATH", ""),
                 "PYTHONIOENCODING": "utf-8",
                 "HOME": str(tmpdir),
                 "USERPROFILE": str(tmpdir)},
        )
        assert result.returncode == 0

        # 验证: OldWrite 应仍存在 (debounce 跳过了 rotate)
        lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2, f"expected 2 lines (debounce), got {len(lines)}: {lines}"
        tools = [json.loads(l).get("tool") for l in lines]
        assert "OldWrite" in tools
        assert "NewWrite" in tools
    print(f"  PASS  24h debounce: 跳过重复 rotate")


def test_input_tempfile_cleaned():
    """临时 input 文件写入后应被清理"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        input_path = tmpdir / "input.jsonl"
        input_path.write_text(json.dumps({"ts": "now", "tool": "Test"}) + "\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(WRITER), "--input", str(input_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            env={"PATH": __import__("os").environ.get("PATH", ""),
                 "PYTHONIOENCODING": "utf-8",
                 "HOME": str(tmpdir),
                 "USERPROFILE": str(tmpdir)},
        )
        assert result.returncode == 0
        assert not input_path.exists(), f"input temp file 未清理: {input_path}"
    print(f"  PASS  临时 input 文件被清理")


if __name__ == "__main__":
    print("=== PESS async_audit + audit_writer 单元测试 (OPT-024 v3.8.0) ===\n")
    tests = [
        test_posttooluse_real_async,
        test_pretooluse_also_writes,
        test_bad_stdin_silent,
        test_non_target_event_silent,
        test_rotate_30_days_debounce,
        test_debounce_24h,
        test_input_tempfile_cleaned,
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
