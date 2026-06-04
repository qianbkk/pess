"""PESS validate_status.py 单元测试 (OPT-014)"""
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

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate_status.py"


def run_validate(status_content: str) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        s = Path(tmp) / "STATUS.md"
        s.write_text(status_content, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(s)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        return result.returncode, result.stdout, result.stderr


def test_valid_status_passes():
    code, stdout, stderr = run_validate("""# Project Status

## Active Features

### CHG-20260605-1430 (PROPOSED)
- Title: test

### CHG-20260604-1000 (APPLYING)
- Title: another

## Recently Archived
""")
    assert code == 0, f"expected 0, got {code}: {stderr}"
    print("  PASS  合法 STATUS.md 验证通过")


def test_invalid_state_fails():
    code, stdout, stderr = run_validate("""# Status
### CHG-XXX (BOGUS)
""")
    assert code != 0
    assert "BOGUS" in stderr
    print("  PASS  非法状态 (BOGUS) 被拒绝")


def test_empty_status_passes():
    code, stdout, stderr = run_validate("# Status\n\n(空项目, 无 features)\n")
    assert code == 0
    print("  PASS  无 features 的空 STATUS 合法")


def test_missing_file_fails():
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), f"{tmp}/nonexistent.md"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr
    print("  PASS  STATUS.md 不存在 → 错误退出")


if __name__ == "__main__":
    print("=== PESS validate_status.py 单元测试 (OPT-014) ===\n")
    tests = [
        test_valid_status_passes,
        test_invalid_state_fails,
        test_empty_status_passes,
        test_missing_file_fails,
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
