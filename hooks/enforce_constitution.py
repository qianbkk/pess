"""PESS UserPromptSubmit 复习宪法 hook (OPT-028, 用户决策独立成卡)

监听 UserPromptSubmit 事件, 在 AI 每次回复前注入 constitution 摘要
到 system context, 防止 AI 偏离项目不可协商原则

独立成卡的决策: 辩论报告 hooks#4 采纳清单,
用户确认独立而非合入 OPT-020 CI 闭环。
"""
import json
import os
import sys
from pathlib import Path

# Windows GBK stdout 修复
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# constitution 注入字符上限 (小, 只放核心红线)
MAX_CONSTITUTION_CHARS = 2000


def find_project_root(start_path: Path = None):
    if start_path is None:
        start_path = Path.cwd()
    for parent in [start_path] + list(start_path.parents)[:8]:
        if (parent / "memory-bank").is_dir():
            return parent
    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    event = data.get("hook_event_name") or data.get("event") or "UserPromptSubmit"
    if event != "UserPromptSubmit":
        sys.exit(0)

    payload_cwd = data.get("cwd")
    start_path = Path(payload_cwd) if payload_cwd else None
    project_root = find_project_root(start_path)
    if not project_root:
        sys.exit(0)

    const_path = project_root / "memory-bank" / "constitution.md"
    if not const_path.is_file():
        sys.exit(0)

    try:
        if const_path.stat().st_size > 100 * 1024:
            sys.exit(0)
        content = const_path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        sys.exit(0)

    if not content:
        sys.exit(0)

    # 截断到上限
    if len(content) > MAX_CONSTITUTION_CHARS:
        content = content[:MAX_CONSTITUTION_CHARS] + "\n\n[truncated]"

    # UserPromptSubmit 协议: 注入到 system context
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"[PESS Constitution — read every turn]\n\n{content}",
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
