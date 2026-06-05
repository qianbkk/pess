"""PESS guard_files.py — PreToolUse 写文件守卫 (v3.8.0 修复)

修复:
- 用 utils.safe_read_stdin() 替代裸 json.loads (B3: fail-open 一致性)
- 接入 whitelist (B2: 不再死代码)
- HARD_BLOCK 永远不白名单 (即使在白名单中也阻断)
- flag 注入防护: file_path 以 '-' 开头静默放行 (B4 一致性)
"""
import json
import os
import sys
from pathlib import Path

# 让 utils 可被 import
sys.path.insert(0, str(Path(__file__).parent))
from utils import safe_read_stdin  # noqa: E402
from whitelist import is_whitelisted, load_whitelist  # noqa: E402

# 极窄的硬阻断范围 (减少误报)
HARD_BLOCK = [".env", ".pem", ".key", ".pfx", "secrets.yaml", "secrets.json"]

# 软警告 (不阻断, 只提示) - SOFT_WARN 路径可被白名单豁免
SOFT_WARN = ["/core/", "/migrations/", "settings.py", "config.py"]


def main():
    data = safe_read_stdin()
    if not data:
        # fail-open: 无 stdin 数据时静默放行
        sys.exit(0)

    path = data.get("tool_input", {}).get("path", "") or data.get("tool_input", {}).get("file_path", "")

    # flag 注入防护 (B4 一致性: 与 auto_lint.py 一致)
    if path.startswith("-"):
        sys.exit(0)

    basename = os.path.basename(path)

    # HARD_BLOCK 永远阻断, 不受白名单影响
    if any(basename.endswith(p) or basename == p for p in HARD_BLOCK):
        print(json.dumps({
            "action": "block",
            "message": f"⛔ 受保护文件: {path}\n如需修改，请在输入中明确说'强制修改 {basename}'"
        }), file=sys.stderr)
        sys.exit(2)

    # SOFT_WARN 路径可被白名单豁免
    is_soft_warn = any(p in path for p in SOFT_WARN)
    if is_soft_warn and not is_whitelisted(path, hard_block=False):
        print(json.dumps({
            "action": "warn",
            "message": f"⚠️  敏感路径: {path}, 请确认操作正确"
        }), file=sys.stderr)
        # 软警告走 stderr (与 auto_lint.py 一致, N6)
        sys.exit(0)

    # 无匹配, 静默放行
    sys.exit(0)


if __name__ == "__main__":
    main()
