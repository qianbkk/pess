# PESS v3.1.0 (2026-05-31)

## What's New

### Memory Bank — Complete 6-File System
- Added `techContext.md` — 技术栈、依赖、工具链
- Added `progress.md` — 已完成/已知问题/下一里程碑
- Refactored `activeContext.md` — now only tracks current task
- `/wrap` now updates `progress.md` automatically

### TDD Enforcement — Testing-Patterns Skill Fixed
- Trigger changed from "创建测试文件时" to "编写任何业务逻辑/API/函数之前"
- Skill now enforces TDD workflow, not just test writing tips

### Cross-Platform Support
- Added `pess-install.sh` — Bash install script for macOS/Linux
- Added `pess-init.sh` — Bash project init script for macOS/Linux

### Structured Checkpoint
- Added structured checklist (lint → test → coverage → Memory Bank sync)
- Added rollback protocol on failure (git stash + failure record)

### Feature Spec Template
- Added `templates/commands/feature-spec.md` — formal spec template
- Use before `/plan` to lock feature intent

### Constitution
- Added `memory-bank/constitution.md` — 项目宪法，不可协商原则

### ADR Template
- Added `templates/adr-template.md` — Architecture Decision Record format

### AGENTS.md — RFC 2119 Format
- Reformatted all rules using MUST/SHOULD/MAY keywords
- Per agent-rules community standard

### Skill Description Audit
- All skill descriptions now contain ONLY triggering conditions
- Workflow steps moved to skill body only

### /think — Enhanced with Red Team
- Structured assumption listing
- Red team challenge section
- Scope confirmation (In/Out/Deferred)

### /plan — Complexity + Task ID
- Complexity scoring (S/M/L/XL)
- Task IDs for cross-reference
- Parallel execution markers

### Guard Hooks Documentation
- README now documents all hook triggers and behaviors

### CHANGELOG + Version Management
- Added `CHANGELOG.md`
- Scripts now report version

---

## Migration from v3.0

Run `pess-install.ps1` (or `pess-install.sh` on macOS/Linux) again to:
1. Update hooks to latest version
2. Deploy new `global-CLAUDE.md` (won't overwrite existing)

New projects: `pess-init -ProjectName "x" -ProjectType "y"` now creates full 6-file Memory Bank.