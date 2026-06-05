"""PESS audit log 后台写入器 (async_audit.py 的子进程)

接收 --input <file.jsonl>, 把内容追加到 ~/.claude/pess-audit.log
- 30 天滚动 (24h debounce: 距上次轮转 < 24h 跳过)
- 写入完成后删除 input 临时文件
- 子进程独立运行, 不阻塞主 hook
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
    except Exception:
        pass

AUDIT_DIR = Path.home() / ".claude"
AUDIT_LOG = AUDIT_DIR / "pess-audit.log"
ROTATE_STATE = AUDIT_DIR / ".pess-audit-last-rotate"
RETENTION_DAYS = 30
ROTATE_DEBOUNCE_HOURS = 24


def rotate_if_needed():
    """30 天滚动 + 24h debounce"""
    if not AUDIT_LOG.is_file():
        return

    # debounce: 24h 内已轮转过则跳过
    if ROTATE_STATE.is_file():
        try:
            last = ROTATE_STATE.stat().st_mtime
            if (time.time() - last) < ROTATE_DEBOUNCE_HOURS * 3600:
                return
        except OSError:
            pass

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
                    ts_str = entry.get("ts", "").rstrip("Z")
                    entry_ts = datetime.fromisoformat(ts_str).timestamp()
                    if entry_ts >= cutoff_ts:
                        kept.append(line)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    except Exception:
        return

    with AUDIT_LOG.open("w", encoding="utf-8") as f:
        for line in kept:
            f.write(line + "\n")

    # 标记 debounce
    try:
        ROTATE_STATE.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--input":
        sys.exit(2)

    input_path = Path(sys.argv[2])
    if not input_path.is_file():
        sys.exit(0)

    # 读取 input
    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception:
        sys.exit(0)

    if not content.strip():
        sys.exit(0)

    # 30 天滚动
    rotate_if_needed()

    # 追加
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"audit_writer: write failed: {e}", file=sys.stderr)
    finally:
        # 清理 input 临时文件
        try:
            input_path.unlink(missing_ok=True)
        except OSError:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
