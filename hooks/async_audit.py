"""PESS async audit log (OPT-024, v3.8.0 修复)

监听 PostToolUse 事件, 异步 (subprocess.Popen) 写入 ~/.claude/pess-audit.log
JSONL 格式: ts/event/tool/path

设计:
- 真正异步: 把 JSON 行通过 stdin 喂给独立子进程 audit_writer.py
- 主 hook 进程立即返回 exit 0, 不阻塞 AI 工具调用
- 子进程在后台串行化写入, 30 天滚动 + 24h debounce
- 隐私: 路径不脱敏 (本地文件, 用户自管)
"""
import json
import os
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

# Windows GBK fixes (Popen 子进程不继承这些)
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
    os.environ.pop(key, None)

AUDIT_DIR = Path.home() / ".claude"
AUDIT_LOG = AUDIT_DIR / "pess-audit.log"
WRITER_SCRIPT = Path(__file__).parent / "audit_writer.py"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    event = data.get("hook_event_name") or data.get("event") or "PostToolUse"
    if event not in ("PostToolUse", "PreToolUse"):
        sys.exit(0)

    tool_name = data.get("tool_name", "?")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("command", "")

    # 写一个临时 JSONL 文件, 让子进程读取后删除
    # (避免 stdin 阻塞, 也不用担心父进程退出后子进程拿不到数据)
    entry = {
        "ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event,
        "tool": tool_name,
        "path": str(file_path)[:500],
    }
    line = json.dumps(entry, ensure_ascii=False)

    # 把 JSON 行写到临时文件, 子进程从文件读
    try:
        # NamedTemporaryFile 在 Windows 上 dir 路径不存在时会失败
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        tmp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".jsonl",
            delete=False, dir=str(AUDIT_DIR),
        )
        tmp.write(line + "\n")
        tmp.close()
    except Exception as e:
        print(f"audit: tmp write failed: {e}", file=sys.stderr)
        sys.exit(0)

    # 真正异步: Popen 子进程, 不 wait, 不 capture
    # 子进程不读父进程 stdin, 所以父进程立即 return
    try:
        # Windows 下 creationflags 避免弹窗
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        # Windows 路径含反斜杠, 必须用 normpath + forward slashes 转 POSIX 形式
        # (Popen 在 Windows 上会按字面意义把 tmp.name 当参数, 反斜杠没问题,
        #  但 list 形式 + 含特殊字符时, 必须确保是绝对路径)
        input_path = os.path.normpath(tmp.name)
        subprocess.Popen(
            [sys.executable, str(WRITER_SCRIPT.resolve()), "--input", input_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
    except Exception as e:
        # Popen 失败, 退化为同步写入
        print(f"audit: Popen failed, fallback to sync: {e}", file=sys.stderr)
        try:
            AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with AUDIT_LOG.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            os.unlink(tmp.name)
        except Exception:
            pass
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
