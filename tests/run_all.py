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
    "test_hooks.py",                # 20 项 — core guards
    "test_auto_lint.py",            # 14 项 — PostToolUse lint
    "test_inject_context.py",       # 11 项 — SessionStart inject
    "test_enforce_constitution.py", # 5 项 — UserPromptSubmit 复习宪法 (OPT-028)
    "test_utils.py",                # 6 项 — stdin JSON 异常处理 (OPT-021)
    "test_engine.py",               # 9 项 — 模板引擎 3 原语 (OPT-013)
    "test_status_validator.py",     # 4 项 — STATUS.md 状态机 (OPT-014)
    "test_async_audit.py",          # 7 项 — 异步 audit + 30 天滚动 (OPT-024 v3.8.0)
    "test_whitelist.py",            # 5 项 — 路径白名单 (OPT-022 v3.8.0)
    "test_pre_stop_check.py",       # 6 项 — Stop 软门禁 (OPT-023 v3.8.0)
]

# 需要 pytest 运行 (因含 fixture-style 测试)
PYTEST_FRAMEWORK_SUITES = [
    "test_pess.py",                 # 9 项 (4 传统 + 5 fixture)
]


def run_suite(suite_name: str) -> bool:
    """运行单个测试套件"""
    suite_path = TESTS_DIR / suite_name
    print(f"\n=== {suite_name} ===")
    if suite_name in PYTEST_FRAMEWORK_SUITES:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite_path), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[-500:])
    else:
        result = subprocess.run(
            [sys.executable, str(suite_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.stdout:
            print(result.stdout)
    return result.returncode == 0


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
    suites = PYTEST_SUITES + PYTEST_FRAMEWORK_SUITES
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
