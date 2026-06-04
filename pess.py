#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PESS 统一 Python 入口 (OPT-012 Phase 1 — skeleton)

设计: 合并 pess-install / pess-init / pess-update 为单一 Python 入口
PS1/Bash 脚本保留为薄 shim 调用 pess.py (向后兼容)

注意: 这是 Phase 1 skeleton, 仅 install 子命令实现完整.
init/update 子命令框架已建, 详细实现留待 Phase 2.
"""
import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Windows GBK fixes
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    os.environ.pop(key, None)


def cmd_install(args) -> int:
    """PESS 全局组件安装 (合并原 pess-install.ps1 逻辑)"""
    pess_root = Path(__file__).resolve().parent
    claude_dir = Path.home() / ".claude"
    hooks_dir = claude_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # 复制 hooks
    hook_files = ["guard_files.py", "guard_commands.py",
                  "auto_lint.py", "inject_context.py", "enforce_constitution.py"]
    for hf in hook_files:
        src = pess_root / "hooks" / hf
        if src.is_file():
            (hooks_dir / hf).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Hooks installed to {hooks_dir}")

    # 合并 settings.json
    settings_path = claude_dir / "settings.json"
    existing = {}
    if settings_path.is_file():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    hooks = existing.setdefault("hooks", {})
    pre = hooks.setdefault("PreToolUse", [])
    post = hooks.setdefault("PostToolUse", [])
    session = hooks.setdefault("SessionStart", [])
    ups = hooks.setdefault("UserPromptSubmit", [])

    # 去重 + 追加
    def has_hook(entries, name):
        for e in entries:
            for h in e.get("hooks", []):
                if name in h.get("command", ""):
                    return True
        return False

    if not has_hook(pre, "guard_files"):
        pre.append({"matcher": "Write|Edit|MultiEdit",
                    "hooks": [{"type": "command", "command": f'python "{hooks_dir}/guard_files.py"'}]})
    if not has_hook(pre, "guard_commands"):
        pre.append({"matcher": "Bash",
                    "hooks": [{"type": "command", "command": f'python "{hooks_dir}/guard_commands.py"'}]})
    if not has_hook(post, "auto_lint"):
        post.append({"matcher": "Write|Edit|MultiEdit",
                     "hooks": [{"type": "command", "command": f'python "{hooks_dir}/auto_lint.py"'}]})
    if not has_hook(session, "inject_context"):
        session.append({"hooks": [{"type": "command", "command": f'python "{hooks_dir}/inject_context.py"'}]})
    if not has_hook(ups, "enforce_constitution"):
        ups.append({"hooks": [{"type": "command", "command": f'python "{hooks_dir}/enforce_constitution.py"'}]})

    settings_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"settings.json updated: {settings_path}")
    return 0


def cmd_init(args) -> int:
    """项目初始化 (Phase 2 占位)"""
    print(f"pess.py init: project={args.project_name} type={args.project_type}")
    print("Note: 完整 init 逻辑见 pess-init.ps1/sh, Phase 2 将迁移")
    return 0


def cmd_update(args) -> int:
    """PESS 更新 (Phase 2 占位)"""
    print("pess.py update: Phase 2 待实施")
    return 0


def cmd_doctor(args) -> int:
    """PESS 健康检查 (Phase 2 占位)"""
    print("pess.py doctor: Phase 2 待实施")
    return 0


def main():
    parser = argparse.ArgumentParser(description="PESS unified Python entry (OPT-012)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="Install PESS global components")
    p_install.set_defaults(func=cmd_install)

    p_init = sub.add_parser("init", help="Initialize a new PESS project")
    p_init.add_argument("-n", "--project-name", required=True)
    p_init.add_argument("-t", "--project-type", default="default")
    p_init.set_defaults(func=cmd_init)

    p_update = sub.add_parser("update", help="Update PESS to latest version")
    p_update.add_argument("--check-only", action="store_true")
    p_update.set_defaults(func=cmd_update)

    p_doctor = sub.add_parser("doctor", help="PESS system health check")
    p_doctor.set_defaults(func=cmd_doctor)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
