# PESS v3.1 — 个人AI编程工程规范系统

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.3.1-00D084.svg)](https://github.com/qianbkk/pess)
[![Claude Code](https://img.shields.io/badge/AI-Claude%20Code-7B42F5?logo=anthropic)](https://claude.ai/code)

**版本：** 3.3.1
**基准日期：** 2026-05-31
**适用工具：** **Claude Code**（本次优化范围；Cursor / GitHub Copilot 跨平台适配计划中，详见 CHANGELOG）
**设计目标：** 让个人开发者在 vibe coding 复杂项目时获得可持续的质量保障

---

## 一句话描述

PESS 是一个 AI 辅助编程工作流规范系统，通过结构化的命令流程（/think → /plan → /checkpoint → /review → /wrap）确保项目质量和可维护性。

---

## 快速安装

### Windows (PowerShell)
```powershell
git clone https://github.com/qianbkk/pess.git D:\PersonalTools\pess
cd D:\PersonalTools\pess
.\pess-install.ps1
```

### macOS / Linux (Bash)
```bash
git clone https://github.com/qianbkk/pess.git ~/pess
cd ~/pess
bash pess-install.sh
```

---

## 项目初始化

### Windows
```powershell
pess-init -ProjectName "my-project" -ProjectType "python-fastapi"
```

### macOS / Linux
```bash
bash pess-init.sh -n my-project -t python-fastapi
```

**项目类型**: `default` / `python-fastapi` / `node-express` / `fullstack` / `simulation`

---

## 核心命令

| 命令 | 用途 | 触发时机 |
|------|------|---------|
| `/think` | 挑战假设 + 红队审查 | 写任何代码之前 |
| `/plan` | 任务分解（带任务ID + 复杂度） | 确认方向后 |
| `/checkpoint` | 质量门控 + 结构化检查清单 | 每完成一个逻辑单元 |
| `/review` | 多维度代码审查 | 提 PR 前 |
| `/wrap` | 会话收尾 + 进度更新 | 结束工作时 |

**可选命令**: `/specify` — 在 /plan 之前生成正式功能规格文档（使用 `templates/commands/feature-spec.md` 模板）

---

## Skills（自动触发）

| Skill | 触发条件 |
|-------|---------|
| security-patterns | 涉及认证/JWT/API密钥/用户输入时 |
| testing-patterns | 编写任何业务逻辑之前（强制 TDD） |
| simulation | LS-DYNA/弹道仿真项目 |
| ato-agent | ATO 多Agent编排项目 |

---

## Memory Bank（6 文件体系）

| 文件 | 用途 |
|------|------|
| `activeContext.md` | 当前任务状态 |
| `progress.md` | 已完成里程碑 / 已知问题 / 下一里程碑 |
| `systemPatterns.md` | 架构决策记录 |
| `lessons.md` | 踩坑记录 |
| `session-notes.md` | 会话笔记（自动写入） |
| `constitution.md` | 项目宪法（不可协商原则） |

**ADR 记录**: `docs/adr/` 目录使用 `templates/adr-template.md` 模板

---

## 安全护盾（Hooks）

通过 `pess-install.ps1` / `pess-install.sh` 安装到用户级：

| 守卫 | 触发 | 行为 |
|------|------|------|
| `guard_files.py` | Write/Edit/MultiEdit 操作受保护文件 | 阻断 .env/.pem/.key/.pfx/secrets.yaml/secrets.json |
| `guard_commands.py` | Bash 执行危险命令 | 阻断 `rm -rf /` / `DROP TABLE` / `/dev/sda` 等 |

---

## 目录结构

```
pess/
├── hooks/                      # 安全守卫（源码）
├── templates/
│   ├── commands/               # /think, /plan, /checkpoint, /review, /wrap, /specify
│   ├── skills/                 # security-patterns, testing-patterns, simulation, ato-agent
│   ├── adr-template.md        # ADR 格式模板
│   ├── constitution.md        # 项目宪法模板
│   ├── default/               # 默认项目 CLAUDE.md
│   ├── python-fastapi/
│   ├── node-express/
│   ├── fullstack/
│   └── simulation/
├── pess-init.ps1 / pess-init.sh    # 项目初始化
├── pess-install.ps1 / pess-install.sh # 全局安装
├── AGENTS.md                  # 跨工具规范（RFC 2119 格式）
├── CHANGELOG.md              # 版本变更记录
└── README.md
```

---

## 判断是否需要某条规范的三问法

1. AI 在过去一个月里至少犯过这个错误一次吗？如果不是 → 不需要
2. 这条内容放 CLAUDE.md 还是 Skills？
3. 在我最忙最赶的那天，我会绕过这个机制还是遵循它？

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

- **Bug 和功能请求**：请提 [GitHub Issue](https://github.com/qianbkk/pess/issues)
- **Pull Request**：fork 仓库，创建分支，完成后提交 PR 即可
- **规范补充**：新增 Skill 或 Command 时，请同步更新本文档对应章节