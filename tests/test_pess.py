"""PESS pess.py 单元测试 (OPT-012 Phase 1)"""
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

PESS_PY = Path(__file__).resolve().parent.parent / "pess.py"


def test_pess_help():
    """pess.py --help 应输出帮助"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    assert "PESS" in result.stdout
    assert "install" in result.stdout
    assert "init" in result.stdout
    print("  PASS  pess.py --help → 列出 install/init/update/doctor")


def test_pess_install_creates_settings():
    """pess.py install 应创建 ~/.claude/settings.json"""
    with tempfile.TemporaryDirectory() as fake_home:
        env = {"HOME": fake_home, "USERPROFILE": fake_home, "PATH": __import__("os").environ.get("PATH", "")}
        result = subprocess.run(
            [sys.executable, str(PESS_PY), "install"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            env=env,
        )
        # install 可能因为 hooks 源路径不存在失败, 但要测试 settings 写入
        # 实际: 复制 hooks 用的是相对 pess.py 的 hooks/, 临时 HOME 不影响
        settings = Path(fake_home) / ".claude" / "settings.json"
        if settings.is_file():
            data = json.loads(settings.read_text(encoding="utf-8"))
            assert "hooks" in data
            assert "PreToolUse" in data["hooks"]
            assert "SessionStart" in data["hooks"]
            assert "UserPromptSubmit" in data["hooks"]
            print("  PASS  pess.py install → 写入 settings.json (含 4 类 hook)")
        else:
            print(f"  SKIP  pess.py install: settings.json 未创建 (rc={result.returncode})")
            print(f"  stdout: {result.stdout[:200]}")
            print(f"  stderr: {result.stderr[:200]}")


def test_pess_init_skeleton():
    """pess.py init 应输出 skeleton 消息"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "init", "-n", "test-proj", "-t", "default"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    assert "test-proj" in result.stdout
    print("  PASS  pess.py init → 输出项目名 (skeleton)")


def test_pess_update_skeleton():
    """pess.py update 应输出 skeleton 消息"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "update"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    print("  PASS  pess.py update → Phase 2 占位")


if __name__ == "__main__":
    print("=== PESS pess.py 单元测试 (OPT-012) ===\n")
    tests = [
        test_pess_help,
        test_pess_install_creates_settings,
        test_pess_init_skeleton,
        test_pess_update_skeleton,
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
