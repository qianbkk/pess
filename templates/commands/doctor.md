---
name: doctor
description: "Use when user wants to check PESS system health. Triggers 5-step local diagnosis: install state, file consistency, template render, git state, STATUS.md schema."
---

# /doctor — PESS 系统健康检查

> **触发条件**: 用户输入 /doctor
> **目的**: 5 步系统健康检查, 输出报告

---

## 步骤 5: STATUS.md 一致性检查 (OPT-025)

如果项目根存在 STATUS.md, 执行:
1. 验证 STATUS.md schema 合法 (调 scripts/validate_status.py)
2. 状态流转无循环 (PROPOSED → APPLYING → TESTING → ARCHIVED)
3. 孤儿 feature 检测 (proposal.md 缺失但 STATUS.md 有该 feature)
4. 状态非法时给出修复建议

> 注: /doctor 是本地版, CI 远端版见 pess-quality.yml Validate STATUS.md step

---

## 第一步：检查 PESS 安装状态

**检查项**（请报告每项结果）：

### 1. Hooks 安装
```bash
ls -la ~/.claude/hooks/ 2>&1 | grep guard
```
预期：显示 `guard_files.py` 和 `guard_commands.py`

### 2. 全局 settings.json
```bash
cat ~/.claude/settings.json 2>&1 | grep -A5 PreToolUse
```
预期：显示两个 PreToolUse matcher 配置

### 3. 全局 CLAUDE.md
```bash
head -5 ~/.claude/CLAUDE.md 2>&1
```
预期：显示 PESS 全局规范内容（不是空的）

---

## 第二步：检查项目初始化状态

**在目标项目目录下运行**：

```bash
echo "=== CLAUDE.md ===" && head -3 CLAUDE.md 2>&1
echo "=== memory-bank ===" && ls memory-bank/ 2>&1
echo "=== Commands ===" && ls .claude/commands/ 2>&1
echo "=== Skills ===" && ls .claude/skills/ 2>&1
```

**预期**：
- CLAUDE.md 存在且非空
- memory-bank/ 包含 6 个文件
- Commands 包含 5+ 个命令文件
- Skills 包含对应项目的 skill 文件

---

## 第三步：检查 Memory Bank 健康度

### activeContext.md 时效性
```bash
grep "更新时间:" memory-bank/activeContext.md 2>&1
```
**警告**：更新时间超过 7 天未更新 → 需要 `/wrap`

### session-notes.md 大小
```bash
wc -l memory-bank/session-notes.md 2>&1
```
**警告**：文件超过 500 行 → 建议归档旧内容

### lessons.md 有内容
```bash
grep -v "^#" memory-bank/lessons.md | grep -v "^$" | wc -l 2>&1
```
**信息**：有多少条实际记录（排除注释和空行）

---

## 第四步：Guard Hooks 测试

```bash
echo "test" | python ~/.claude/hooks/guard_files.py 2>&1
echo "echo hello" | python ~/.claude/hooks/guard_commands.py 2>&1
```
预期：两项都输出 `{}` 或退出码 0（不阻断）

---

## 输出格式

请按以下格式报告检查结果：
```
/doctor 检查报告

Hooks:
  guard_files.py:     [存在/缺失]
  guard_commands.py:   [存在/缺失]
  settings.json:       [正常/异常]

项目:
  CLAUDE.md:           [存在/缺失]
  Memory Bank 文件数:  [数量] / 6
  Commands 文件数:     [数量]
  Skills 文件数:       [数量]

健康度:
  activeContext 更新:  [日期/过期警告]
  session-notes 大小:  [行数/需归档]
  lessons 记录数:     [数量]

Guards:
  guard_files:         [正常/异常]
  guard_commands:      [正常/异常]
```