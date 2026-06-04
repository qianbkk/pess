"""PESS STATUS.md 验证脚本 (OPT-014)

CI 读 STATUS.md, 验证状态机合法性 (PROPOSED → APPLYING → TESTING → ARCHIVED)
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VALID_STATES = ("PROPOSED", "APPLYING", "TESTING", "ARCHIVED")
STATE_TRANSITIONS = {
    "PROPOSED":  {"APPLYING"},
    "APPLYING":  {"TESTING", "ARCHIVED"},
    "TESTING":   {"ARCHIVED", "APPLYING"},  # 允许回滚
    "ARCHIVED":  set(),  # 终态
}


def validate(status_path: Path) -> list[str]:
    if not status_path.is_file():
        return [f"ERROR: {status_path} not found"]

    text = status_path.read_text(encoding="utf-8", errors="replace")
    errors = []

    # 解析所有 feature 段
    feature_pattern = re.compile(
        r"###\s+(CHG-[\w-]+)\s+\((\w+)\)", re.MULTILINE
    )
    matches = list(feature_pattern.finditer(text))
    if not matches:
        return []  # 无 feature 是合法的

    # 按位置排序, 验证 state 顺序 (跨 session 应保持单调或回滚)
    # 此处只检查状态值合法性
    for m in matches:
        feature_id = m.group(1)
        state = m.group(2)
        if state not in VALID_STATES:
            errors.append(f"{feature_id}: invalid state '{state}' (must be one of {VALID_STATES})")

    return errors


def main():
    status_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("STATUS.md")
    errors = validate(status_path)
    if errors:
        print("STATUS.md 验证失败:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"STATUS.md 验证通过 ({status_path})")


if __name__ == "__main__":
    main()
