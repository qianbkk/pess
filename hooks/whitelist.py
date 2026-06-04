"""PESS guard_files.py 白名单机制 (OPT-022)

读取 ~/.claude/pess-whitelist.json (如存在), 路径在白名单时跳过 HARD_BLOCK

默认白名单 (无需配置): .pess-test/ .pess-sandbox/
限制: 白名单只对 SOFT_WARN 生效, HARD_BLOCK (.env/.pem) 永远不白名单
"""
import json
from pathlib import Path

WHITELIST_PATH = Path.home() / ".claude" / "pess-whitelist.json"
DEFAULT_WHITELIST = [".pess-test/", ".pess-sandbox/"]


def load_whitelist() -> list[str]:
    if WHITELIST_PATH.is_file():
        try:
            data = json.loads(WHITELIST_PATH.read_text(encoding="utf-8"))
            return list(data.get("paths", []))
        except (json.JSONDecodeError, OSError):
            return DEFAULT_WHITELIST
    return DEFAULT_WHITELIST


def is_whitelisted(file_path: str, hard_block: bool = False) -> bool:
    """路径是否在白名单 (hard_block 永远不被白名单)"""
    if hard_block:
        return False
    for pattern in load_whitelist():
        if file_path.startswith(pattern) or file_path == pattern.rstrip("/"):
            return True
    return False
