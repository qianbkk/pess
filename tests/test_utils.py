"""PESS hooks/utils.py 单元测试 (OPT-021)"""
import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from utils import safe_read_stdin


def test_normal_json():
    sys.stdin = io.StringIO('{"a": 1}')
    assert safe_read_stdin() == {"a": 1}
    print("  PASS  正常 JSON → parsed dict")


def test_empty_stdin():
    sys.stdin = io.StringIO("")
    assert safe_read_stdin() == {}
    print("  PASS  空 stdin → {}")


def test_invalid_json():
    sys.stdin = io.StringIO("not valid json")
    assert safe_read_stdin() == {}
    print("  PASS  非法 JSON → {} (fail-open)")


def test_truncated_json():
    sys.stdin = io.StringIO('{"a": "b')
    assert safe_read_stdin() == {}
    print("  PASS  截断 JSON → {} (fail-open)")


def test_huge_json():
    """10MB+ stdin 应被防护跳过"""
    huge = '{"a": "' + "x" * (11 * 1024 * 1024) + '"}'
    sys.stdin = io.StringIO(huge)
    assert safe_read_stdin() == {}
    print("  PASS  10MB+ stdin → {} (防护 OOM)")


def test_unicode_in_json():
    sys.stdin = io.StringIO('{"name": "测试"}')
    result = safe_read_stdin()
    assert result.get("name") == "测试"
    print("  PASS  Unicode JSON → parsed")


if __name__ == "__main__":
    print("=== PESS utils.py 单元测试 (OPT-021) ===\n")
    tests = [
        test_normal_json,
        test_empty_stdin,
        test_invalid_json,
        test_truncated_json,
        test_huge_json,
        test_unicode_in_json,
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
