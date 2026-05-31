# PESS — Personal Engineering Standards System

> 让个人开发者在 AI 辅助复杂项目时获得可持续的质量保障

---

## 系统架构

PESS 由 4 个核心组件构成：

### Commands（结构化工作流）
| 命令 | 用途 | 触发时机 |
|------|------|---------|
| `/think` | 挑战假设 + 红队审查 | 写任何代码之前 |
| `/plan` | 任务分解（T-001 + 复杂度 + 并行波次） | 确认方向后 |
| `/checkpoint` | 质量门控（覆盖率门控 + 回滚协议） | 每完成一个逻辑单元 |
| `/review` | 多维度审查（正确性/规范/安全/测试） | 提 PR 前 |
| `/wrap` | 会话收尾（自动更新 progress.md） | 结束工作时 |
| `/specify` | 功能规格文档（User Story + Task List + Test Strategy） | 在 /plan 之前 |

### Skills（自动触发，无命令调用）
| Skill | 触发条件 |
|-------|---------|
| `security-patterns` | 涉及认证/JWT/API密钥/用户输入时 |
| `testing-patterns` | 编写任何业务逻辑之前（强制 TDD） |
| `simulation` | LS-DYNA/弹道仿真项目 |
| `ato-agent` | ATO 多Agent编排项目 |

### Memory Bank（6 文件，跨会话持久化）
| 文件 | 用途 |
|------|------|
| `activeContext.md` | 当前任务状态（每会话更新） |
| `progress.md` | 已完成里程碑 / 已知问题 / 下一里程碑 |
| `systemPatterns.md` | 架构决策记录（ADR 风格） |
| `lessons.md` | 踩坑记录（/wrap 自动添加） |
| `session-notes.md` | 会话笔记（/wrap 自动写入，无需手动维护） |
| `constitution.md` | 项目宪法（不可协商的质量底线 + 安全红线） |

### Hooks（自动防护，pess-install.ps1 安装）
| 守卫 | 触发 | 行为 |
|------|------|------|
| `guard_files.py` | Write/Edit/MultiEdit 操作 | 阻断 `.env`/`.pem`/`.key`/`.pfx`/secrets.yaml/secrets.json |
| `guard_commands.py` | Bash 执行 | 阻断 `rm -rf /` / `DROP TABLE` / `/dev/sda` 等危险命令 |

---

## 修改规则

- `templates/` 下的文件是只读模板，修改时必须考虑所有使用了该模板的项目
- `hooks/` 下的脚本需要保持与 `pess-install.ps1` 中的路径一致
- 任何新增的 Skill 必须有符合触发器格式的 `description` 字段（只写触发条件，不写工作流摘要）

## 禁令

- 禁止用 LLM 自动生成任何模板内容
- 禁止在 `templates/` 里写死绝对路径
- 禁止修改 `hooks/` 的文件名（pess-install.ps1 依赖这些名字）

## 判断是否需要某条规范的三问法

1. AI 在过去一个月里至少犯过这个错误一次吗？如果不是 → 不需要
2. 这条内容放 CLAUDE.md 还是 Skills？
3. 在我最忙最赶的那天，我会绕过这个机制还是遵循它？

---

## 快速参考

```bash
# 安装 PESS 全局组件（Windows）
.\pess-install.ps1

# 初始化新项目
pess-init -ProjectName "my-project" -ProjectType "python-fastapi"
#   项目类型: default / python-fastapi / node-express / fullstack / simulation

# 更新 PESS
.\pess-update.ps1 -CheckOnly   # 检查版本
.\pess-update.ps1              # 更新到最新
```

---

*v3.3.2 | https://github.com/qianbkk/pess*