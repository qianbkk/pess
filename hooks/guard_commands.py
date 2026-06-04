import json, sys, re

data = json.loads(sys.stdin.read())
cmd = data.get("tool_input", {}).get("command", "")

# 硬阻断：极窄，只拦真正高危，避免误报
HARD_BLOCK_RE = [
    r"rm\s+-rf\s+[/~]",               # 删除根目录或家目录
    r"DROP\s+(?:TABLE|DATABASE)\s",    # SQL 删除操作（带空格，减少误报）
    r">\s*/dev/(?:sda|sdb|nvme\d)",   # 直写磁盘设备
]

# 软警告：常见误操作，提醒但不阻断
SOFT_WARN_RE = [
    r"git\s+push\s+.*--force",         # 任何形式的 force push
    r"npm\s+publish",
    r"pip\s+install.*--break-system",
    r"kubectl\s+delete",
]

for pattern in HARD_BLOCK_RE:
    if re.search(pattern, cmd, re.IGNORECASE):
        # 修复：Claude Code PreToolUse 协议下 exit 0 = 放行，必须 exit 2 才能阻断
        print(json.dumps({"action": "block",
                          "message": f"⛔ 危险命令已拦截: {cmd}\n请手动执行此操作"}),
              file=sys.stderr)
        sys.exit(2)

for pattern in SOFT_WARN_RE:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(json.dumps({"action": "warn",
                          "message": f"⚠️  请确认此命令: {cmd}"}))
        break

sys.exit(0)