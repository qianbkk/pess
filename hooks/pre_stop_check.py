"""PESS Stop 软门禁 (OPT-023)

Stop 事件触发: AI 声称'完成'前是否:
(a) 跑了测试
(b) 看输出
(c) 验证不变量
(d) 显式确认

默认 soft_warn (不阻断, 仅 stderr 提示)
用户在 settings.json 可配 mode: hard_block
"""
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# AI 输出"完成"类信号词
COMPLETION_SIGNALS = ["完成", "完成", "done", "finished", "搞定了", "可以 merge", "ready to ship"]


def check_test_run_recently() -> bool:
    """检查 5 分钟内是否跑过 pytest/npm test"""
    cutoff = __import__("time").time() - 300
    # 简化: 查找 .pytest_cache 或 coverage 文件
    for marker in [".pytest_cache", ".coverage", "coverage/lcov.info"]:
        p = Path.cwd() / marker
        if p.exists() and p.stat().st_mtime > cutoff:
            return True
    return False


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    event = data.get("hook_event_name") or data.get("event") or "Stop"
    if event != "Stop":
        sys.exit(0)

    # 检查 AI 最后输出是否含完成信号
    last_msg = data.get("last_assistant_message", "") or ""
    if not any(sig.lower() in last_msg.lower() for sig in COMPLETION_SIGNALS):
        # 无完成信号, 不警告
        sys.exit(0)

    # 跑了测试吗？
    if check_test_run_recently():
        sys.exit(0)

    # 默认 soft_warn
    mode = os.environ.get("PESS_STOP_MODE", "soft_warn")
    if mode == "hard_block":
        print("⚠️  Stop 阻断: AI 声称完成但 5 分钟内未跑测试", file=sys.stderr)
        sys.exit(2)
    else:
        print("⚠️  Stop soft_warn: AI 声称'完成'但 5 分钟内未检测到测试运行", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
