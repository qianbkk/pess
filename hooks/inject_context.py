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
# 单文件硬上限 (防恶意用户写 100MB memory-bank 卡住 SessionStart)
MAX_FILE_BYTES = 1 * 1024 * 1024  # 1MB
# 注入的文件列表 (按重要性排序: constitution 优先因为是不可协商底线)
INJECT_FILES = [
    "constitution.md",     # 不可协商底线, 最重要
    "activeContext.md",    # 当前任务状态
    "progress.md",         # 进度追踪
    "techContext.md",      # 技术栈
    "systemPatterns.md",   # 架构模式
    "lessons.md",          # 踩坑记录
    "session-notes.md",    # 会话笔记 (放最后避免冲淡)
]


def find_project_root(start_path: Path = None):
    """从 start_path 向上查找 memory-bank/ 目录, 最多 8 层

    优先用 stdin payload 中的 cwd (Claude Code 官方字段),
    fallback 到 Path.cwd() (独立调用场景).
    """
    if start_path is None:
        start_path = Path.cwd()
    # 强信号优先: 含 .git/ 的目录视为项目根
    for parent in [start_path] + list(start_path.parents)[:8]:
        if (parent / "memory-bank").is_dir():
            return parent
    return None


def read_file_safe(path: Path) -> str:
    """读取文件, 异常静默处理

    设计: 权限错误/IO 错误都被掩盖 (个人开发者工具, 单点降级)
    """
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return f"# [skipped: file > {MAX_FILE_BYTES} bytes]"
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def truncate_smart(text: str, max_chars: int, filename: str) -> str:
    """per-file 智能截断, 在文件边界或段落边界优先切分

    避免切到 markdown 块中间 (代码块/表格/链接)
    """
    if len(text) <= max_chars:
        return text
    # 尝试在最后一个段落边界 (\n\n) 处切
    cut = text[:max_chars]
    last_para = cut.rfind("\n\n")
    if last_para > max_chars * 0.7:  # 至少保留 70% 内容
        cut = cut[:last_para]
    return f"{cut}\n\n[truncated: {filename} > {max_chars} chars]"


def build_context(project_root: Path) -> str:
    """从 memory-bank 收集内容, per-file 截断, 拼接为 system context 字符串

    预算分配 (按重要性):
    - constitution: 25% (不可协商)
    - activeContext: 20% (当前任务)
    - progress: 15%
    - techContext: 15%
    - 其余: 各 10-15%
    """
    memory_bank = project_root / "memory-bank"
    if not memory_bank.is_dir():
        return ""

    # 预算分配 (总 MAX_CHARS 拆分给各文件)
    weights = {
        "constitution.md": 0.25,
        "activeContext.md": 0.20,
        "progress.md": 0.15,
        "techContext.md": 0.15,
        "systemPatterns.md": 0.10,
        "lessons.md": 0.08,
        "session-notes.md": 0.07,
    }

    sections = []
    for filename in INJECT_FILES:
        file_path = memory_bank / filename
        if not file_path.is_file():
            continue
        content = read_file_safe(file_path).strip()
        if not content:
            continue
        budget = int(MAX_CHARS * weights.get(filename, 0.10))
        content = truncate_smart(content, budget, filename)
        sections.append(f"## {filename}\n\n{content}")

    if not sections:
        return ""

    full = "\n\n---\n\n".join(sections)
    if len(full) > MAX_CHARS:
        full = full[:MAX_CHARS] + f"\n\n[truncated at {MAX_CHARS} chars]"
    return full


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    # SessionStart 事件
    event = data.get("hook_event_name") or data.get("event") or "SessionStart"
    if event != "SessionStart":
        sys.exit(0)

    # 优先用 stdin payload 的 cwd (B1 修复), fallback 到 Path.cwd()
    payload_cwd = data.get("cwd")
    start_path = Path(payload_cwd) if payload_cwd else None

    project_root = find_project_root(start_path)
    if not project_root:
        sys.exit(0)

    context = build_context(project_root)
    if not context:
        sys.exit(0)

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
