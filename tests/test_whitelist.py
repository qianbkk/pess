"""PESS hooks/whitelist.py 单元测试 (OPT-022, v3.8.0 修复)"""
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

WHITELIST = Path(__file__).resolve().parent.parent / "hooks" / "whitelist.py"


def run_python(args: list, stdin: str = "") -> tuple[int, str, str]:
    env = __import__("os").environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable] + args,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def test_default_whitelist_contains_pess_test():
    """默认白名单含 .pess-test/ 和 .pess-sandbox/"""
    code, stdout, _ = run_python(
        ["-c",
         "import sys; sys.path.insert(0, r'D:/AI/Claude code workspace/A6.1/PESS/hooks'); "
         "from whitelist import load_whitelist; "
         "wl = load_whitelist(); "
         "print('OK' if '.pess-test/' in wl and '.pess-sandbox/' in wl else 'FAIL')"],
    )
    assert "OK" in stdout
    print("  PASS  默认白名单含 .pess-test/ 和 .pess-sandbox/")


def test_hard_block_never_whitelisted():
    """HARD_BLOCK 永远不被白名单 (即使在白名单中也返回 False)"""
    code, stdout, _ = run_python(
        ["-c",
         "import sys; sys.path.insert(0, r'D:/AI/Claude code workspace/A6.1/PESS/hooks'); "
         "from whitelist import is_whitelisted; "
         "print('OK' if not is_whitelisted('/app/.env', hard_block=True) else 'FAIL')"],
    )
    assert "OK" in stdout
    print("  PASS  HARD_BLOCK (.env) 永远不被白名单")


def test_soft_warn_path_whitelisted():
    """SOFT_WARN 路径在白名单时返回 True (可豁免警告)"""
    code, stdout, _ = run_python(
        ["-c",
         "import sys; sys.path.insert(0, r'D:/AI/Claude code workspace/A6.1/PESS/hooks'); "
         "from whitelist import is_whitelisted; "
         "print('OK' if is_whitelisted('/app/.pess-test/core/db.py', hard_block=False) else 'FAIL')"],
    )
    assert "OK" in stdout
    print("  PASS  .pess-test/ 下的 SOFT_WARN 路径被白名单")


def test_soft_warn_path_not_whitelisted():
    """SOFT_WARN 路径不在白名单时返回 False"""
    code, stdout, _ = run_python(
        ["-c",
         "import sys; sys.path.insert(0, r'D:/AI/Claude code workspace/A6.1/PESS/hooks'); "
         "from whitelist import is_whitelisted; "
         "print('OK' if not is_whitelisted('/app/core/db.py', hard_block=False) else 'FAIL')"],
    )
    assert "OK" in stdout
    print("  PASS  普通 SOFT_WARN 路径不在白名单")


def test_user_whitelist_json_loadable():
    """用户 ~/.claude/pess-whitelist.json 可被加载"""
    with tempfile.TemporaryDirectory() as tmp:
        claude_dir = Path(tmp) / ".claude"
        claude_dir.mkdir()
        whitelist_json = claude_dir / "pess-whitelist.json"
        whitelist_json.write_text('{"paths": ["/custom/path/"]}', encoding="utf-8")

        code, stdout, _ = run_python(
            ["-c",
             f"import sys, os; os.environ['HOME']=r'{tmp}'; os.environ['USERPROFILE']=r'{tmp}'; "
             "sys.path.insert(0, r'D:/AI/Claude code workspace/A6.1/PESS/hooks'); "
             "from whitelist import load_whitelist; print(','.join(load_whitelist()))"],
        )
        assert "/custom/path/" in stdout
    print("  PASS  用户自定义 pess-whitelist.json 可被加载")


if __name__ == "__main__":
    print("=== PESS whitelist.py 单元测试 (OPT-022 v3.8.0) ===\n")
    tests = [
        test_default_whitelist_contains_pess_test,
        test_hard_block_never_whitelisted,
        test_soft_warn_path_whitelisted,
        test_soft_warn_path_not_whitelisted,
        test_user_whitelist_json_loadable,
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
