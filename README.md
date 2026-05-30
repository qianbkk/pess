# PESS v3.0 — 个人AI编程工程规范系统

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0-00D084.svg)](https://github.com/qianbkk/pess)
[![Claude Code](https://img.shields.io/badge/AI-Claude%20Code-7B42F5?logo=anthropic)](https://claude.ai/code)

**版本：** 3.0
**基准日期：** 2026-05-30
**适用工具：** Claude Code（主力）/ Cursor / GitHub Copilot
**设计目标：** 让个人开发者在 vibe coding 复杂项目时获得可持续的质量保障

---

## 一句话描述

PESS 是一个 AI 辅助编程工作流规范系统，通过结构化的命令流程（/think → /plan → /checkpoint → /review → /wrap）确保项目质量和可维护性。

---

## 快速安装

```powershell
# 克隆仓库
git clone https://github.com/qianbkk/pess.git D:\PersonalTools\pess

# 进入目录
cd D:\PersonalTools\pess

# 查看初始化脚本帮助
Get-Help .\pess-init.ps1
```

---

## 本地安装

1. 复制 PESS 文件夹到 `D:\PersonalTools\pess\`
2. 将 `pess-init.ps1` 加入 PATH 或创建别名

```powershell
# 在 PowerShell profile 里添加别名
notepad $PROFILE
# 添加这一行：
function pess-init { & "D:\PersonalTools\pess\pess-init.ps1" @args }
```

## 使用方式

```powershell
# 初始化新项目
pess-init -ProjectName "my-project" -ProjectType "python-fastapi"

# 项目类型选项
# - default:       通用项目
# - python-fastapi: Python FastAPI 项目
# - node-express:  Node.js Express 项目
# - fullstack:     全栈项目
# - simulation:    仿真项目
```

## 目录结构

```
pess/
├── hooks/
│   ├── guard_files.py          # 文件保护守卫
│   └── guard_commands.py       # 命令守卫
├── templates/
│   ├── commands/               # /think, /plan, /checkpoint, /review, /wrap
│   ├── skills/                 # security-patterns, testing-patterns
│   ├── default/                # 默认项目 CLAUDE.md 模板
│   ├── python-fastapi/         # Python FastAPI 项目模板
│   └── simulation/             # 仿真项目模板
├── pess-init.ps1               # 项目初始化脚本
├── AGENTS.md                  # 跨工具规范
└── README.md
```

## 核心命令

| 命令 | 用途 | 触发时机 |
|------|------|---------|
| `/think` | 挑战假设 | 写任何代码之前 |
| `/plan` | 任务分解 | 确认方向后 |
| `/checkpoint` | 质量门控+提交 | 每完成一个逻辑单元 |
| `/review` | 多维代码审查 | 提 PR 前 |
| `/wrap` | 会话收尾 | 结束工作时 |

## Skills（自动触发）

| Skill | 触发条件 |
|-------|---------|
| security-patterns | 涉及 auth/JWT/API/用户输入时 |
| testing-patterns | 创建测试文件时 |
| simulation | LS-DYNA/弹道仿真时 |

## Memory Bank

- `activeContext.md` - 当前任务状态
- `systemPatterns.md` - 架构决策
- `lessons.md` - 踩坑记录（人工确认后写入）
- `session-notes.md` - 会话笔记（自动写入）

## 判断是否需要某条规范的三问法

1. AI 在过去一个月里至少犯过这个错误一次吗？如果不是 → 不需要
2. 这条内容放 CLAUDE.md 还是 Skills？
3. 在我最忙最赶的那天，我会绕过这个机制还是遵循它？

## 贡献指南

欢迎提交 Issue 和 Pull Request！

- **Bug 和功能请求**：请提 [GitHub Issue](https://github.com/qianbkk/pess/issues)
- **Pull Request**：fork 仓库，创建分支，完成后提交 PR 即可
- **规范补充**：新增 Skill 或 Command 时，请同步更新本文档对应章节