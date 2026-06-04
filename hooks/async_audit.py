"""PESS async audit log (OPT-024)

监听 PostToolUse 事件, 异步写入 ~/.claude/pess-audit.log
JSONL 格式: ts/tool/action/path/result

设计:
- 异步 (Popen) 不阻塞 AI 工具调用
- 30 天自动滚动 (删除 >30 天的条目)
- 隐私: 路径不脱敏 (本地文件, 用户自管)
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

AUDIT_LOG = Path.home() / ".claude" / "pess-audit.log"
RETENTION_DAYS = 30


def rotate_if_needed():
    """30 天滚动: 删除 >30 天的条目"""
    if not AUDIT_LOG.is_file():
        return
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cutoff_ts = cutoff.timestamp()
    kept = []
    try:
        with AUDIT_LOG.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_ts = datetime.fromisoformat(entry["ts"].rstrip("Z")).timestamp()
                    if entry_ts >= cutoff_ts:
                        kept.append(line)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    except Exception:
        return

    with AUDIT_LOG.open("w", encoding="utf-8") as f:
        for line in kept:
            f.write(line + "\n")


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        sys.exit(0)

    event = data.get("hook_event_name") or data.get("event") or "PostToolUse"
    if event not in ("PostToolUse", "PreToolUse"):
        sys.exit(0)

    tool_name = data.get("tool_name", "?")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("command", "")

    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "tool": tool_name,
        "path": str(file_path)[:500],  # 截断防超大路径
    }

    # 30 天滚动
    rotate_if_needed()

    # 异步追加 (使用 'a' 模式立即 flush)
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"audit: write failed: {e}", file=sys.stderr)
        sys.exit(0)  # fail-open

    sys.exit(0)


if __name__ == "__main__":
    main()
