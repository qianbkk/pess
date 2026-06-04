"""PESS 统一测试运行器 (OPT-006/007 整合)

将分散的 pytest 文件整合为单一入口, 跨平台 (Windows/Linux/macOS) 统一调用:
- tests/test_hooks.py: 20 项 — guard_files + guard_commands 17 规则 + 退出码协议
- tests/test_auto_lint.py: 14 项 — PostToolUse lint hook
- tests/test_inject_context.py: 11 项 — SessionStart memory-bank 注入
- tests/test-init.ps1: 项目初始化集成 (PowerShell)

用法:
  python tests/run_all.py                 # 跑所有 pytest 套件
  python tests/run_all.py --hooks-only    # 只跑 hook 测试
"""
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

TESTS_DIR = Path(__file__).resolve().parent
PYTEST_SUITES = [
    "test_hooks.py",          # 20 项 — core guards
    "test_auto_lint.py",      # 14 项 — PostToolUse lint
    "test_inject_context.py", # 11 项 — SessionStart inject
]


def run_suite(suite_name: str) -> bool:
    """运行单个 pytest 套件, 返回是否全部通过"""
    suite_path = TESTS_DIR / suite_name
    print(f"\n=== {suite_name} ===")
    result = subprocess.run(
        [sys.executable, str(suite_path)],
        capture_output=False,
        timeout=60,
    )
    return result.returncode == 0


def main():
    args = sys.argv[1:]
    suites = PYTEST_SUITES
    if "--hooks-only" in args:
        suites = ["test_hooks.py"]

    print(f"PESS 统一测试运行器 — 共 {len(suites)} 个套件")
    results = {}
    for suite in suites:
        results[suite] = run_suite(suite)

    print("\n" + "=" * 50)
    print("汇总:")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for suite, ok in results.items():
        marker = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {marker}  {suite}")
    print(f"\n总计: {passed}/{total} 套件通过")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
