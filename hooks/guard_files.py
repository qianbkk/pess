import json, sys, os

data = json.loads(sys.stdin.read())
path = data.get("tool_input", {}).get("path", "")
basename = os.path.basename(path)

# 极窄的硬阻断范围（减少误报）
HARD_BLOCK = [".env", ".pem", ".key", ".pfx", "secrets.yaml", "secrets.json"]

# 软警告（不阻断，只提示）
SOFT_WARN = ["/core/", "/migrations/", "settings.py", "config.py"]

if any(basename.endswith(p) or basename == p for p in HARD_BLOCK):
    # 修复：Claude Code PreToolUse 协议下 exit 0 = 放行，必须 exit 2 才能阻断
    print(json.dumps({
        "action": "block",
        "message": f"⛔ 受保护文件: {path}\n如需修改，请在输入中明确说'强制修改 {basename}'"
    }), file=sys.stderr)
    sys.exit(2)

if any(p in path for p in SOFT_WARN):
    print(json.dumps({
        "action": "warn",
        "message": f"⚠️  敏感路径: {path}，请确认操作正确"
    }))

sys.exit(0)