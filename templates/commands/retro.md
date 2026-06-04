# /retro — 工程回顾 (OPT-024 消费层)

> **触发条件**: 用户输入 /retro [N天] (默认 7 天)
> **目的**: 从 audit.log 统计 7/30 天的命令频次、文件修改热区、guard 拦截率

---

## 工作流程

### 1. 读取 audit.log

```bash
~/.claude/pess-audit.log  # JSONL 格式
```

### 2. 统计维度

| 维度 | 说明 |
|------|------|
| 命令频次 | 按 tool_name 分组, top 10 |
| 文件热区 | path 前缀聚合, top 10 修改最多的目录 |
| Guard 拦截率 | guard_files / guard_commands 触发次数 / 总数 |
| 会话活跃度 | 按 ts 分组, 每天的 audit 条目数 |

### 3. 输出格式

```
=== PESS 工程回顾 (过去 7 天) ===

📊 总览
- Audit 条目: 1,234 条
- 活跃天数: 5/7 天
- 工具调用: 850 次

🛠️  Top 5 命令
- Bash         450 次 (53%)
- Write        220 次 (26%)
- Edit         180 次 (21%)

📁  Top 5 文件热区
- src/api/        120 次
- tests/           95 次
- memory-bank/     60 次

🛡️  Guard 拦截
- guard_files:    3 次 (.env/.key 尝试)
- guard_commands: 1 次 (rm -rf 尝试)

💡 洞察
- 建议: 频繁的 .env 尝试 → 检查团队凭据管理
- 建议: 集中修改 src/api/ → 考虑拆分子模块
```

### 4. 失败处理

- audit.log 不存在: 提示 "无审计数据, 请先使用 PESS 一段时间"
- audit.log < 100 行: 数据不足, 输出简化版
