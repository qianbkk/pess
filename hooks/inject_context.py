"""PESS SessionStart 注入 memory-bank hook (OPT-005)

监听 SessionStart 事件, 读取项目根 memory-bank/activeContext.md + progress.md
追加到 system context (stdout JSON additionalContext 字段, Claude Code 协议)
文件不存在时静默返回; 注入限制 8000 tokens 防超限
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

# 8000 tokens ≈ 32000 chars (粗略: 1 token ≈ 4 chars)
MAX_CHARS = int(os.environ.get("PESS_INJECT_MAX_CHARS", "32000"))
# 注入的文件列表 (按优先级排序)
INJECT_FILES = ["activeContext.md", "progress.md", "constitution.md", "lessons.md", "techContext.md", "systemPatterns.md"]


def find_project_root():
    """从 cwd 向上查找 memory-bank/ 目录, 最多 5 层"""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents)[:5]:
        if (parent / "memory-bank").is_dir():
            return parent
    return None


def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def build_context(project_root: Path) -> str:
    """从 memory-bank 收集内容, 拼接为 system context 字符串"""
    memory_bank = project_root / "memory-bank"
    if not memory_bank.is_dir():
        return ""

    sections = []
    for filename in INJECT_FILES:
        file_path = memory_bank / filename
        if not file_path.is_file():
            continue
        content = read_file_safe(file_path).strip()
        if not content:
            continue
        sections.append(f"## {filename}\n\n{content}")

    if not sections:
        return ""

    full = "\n\n---\n\n".join(sections)
    # 截断到 MAX_CHARS
    if len(full) > MAX_CHARS:
        full = full[:MAX_CHARS] + f"\n\n[truncated at {MAX_CHARS} chars]"
    return full


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    # SessionStart 事件, 也支持其他上下文注入事件
    event = data.get("hook_event_name") or data.get("event") or "SessionStart"
    if event != "SessionStart":
        sys.exit(0)

    project_root = find_project_root()
    if not project_root:
        # 无 memory-bank 目录, 静默通过
        sys.exit(0)

    context = build_context(project_root)
    if not context:
        sys.exit(0)

    # Claude Code SessionStart 协议: stdout JSON 包含 additionalContext 字段
    # 会被注入到 system prompt
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"[PESS Memory Bank — auto-injected from {project_root.name}]\n\n{context}",
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
