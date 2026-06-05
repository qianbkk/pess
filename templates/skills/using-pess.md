---
name: using-pess
description: "Load when user is working on a PESS-initialized project (presence of memory-bank/ directory). Do not load for non-PESS projects. Provides PESS workflow navigation, command selection, and three-question method for adding new conventions."
---

# PESS 使用指南 (using-pess skill, OPT-010)

## 第一段: 何时加载

**触发条件**: 当前工作目录含 `memory-bank/` 子目录

**不要加载**:
- 全新项目 (无 memory-bank/)
- 仅使用 PESS 工具但项目本身不用 PESS 工作流

---

## 第二段: 三问法 (添加任何新规范前必走)

| # | 问题 | 否 → 动作 |
|---|------|----------|
| 1 | AI 在过去一个月里至少犯过这个错误一次吗？ | 不需要此规范 |
| 2 | 放 CLAUDE.md 还是 Skills？ | Skills (按需加载) |
| 3 | 最忙那天会绕过还是遵循？ | 改写为强制 (hook) |

---

## 第三段: 6 个命令的触发决策树

```
写任何代码之前
└─ /think (挑战假设)

→ 写正式功能规格
   └─ 手动生成 spec.md (或等 /specify 计划)
      └─ /clarify (消除模糊)

→ 任务分解
   └─ /plan (T-001 + 复杂度 + 波次)

→ 实施中 (每完成一个逻辑单元)
   └─ /checkpoint (覆盖率门控 + 回滚)

→ 提 PR 前
   └─ /review (多维审查)

→ 收工
   └─ /wrap (更新 progress.md)
```

---

## 第四段: 自检清单 (每日工作流开始时)

- [ ] 读取 `memory-bank/activeContext.md` 知道当前状态
- [ ] 读取 `memory-bank/progress.md` 知道下一步里程碑
- [ ] 读取 `memory-bank/constitution.md` 知道不可协商底线
- [ ] 跑 `/doctor` 验证 PESS 系统健康

---

## 第五段: 错误恢复

| 症状 | 修复 |
|------|------|
| AI 跳过 /think 直接写代码 | 提醒三问法, 用户在 CLAUDE.md 加 MUST |
| /plan 输出无 Test First 子任务 | /plan TDD 强制失败, 检查 plan.md v3.5 |
| /checkpoint 漏覆盖率 | 跑 `pytest --cov` 补报告 |
| progress.md 不更新 | /wrap 时显式说 "更新 progress.md" |
