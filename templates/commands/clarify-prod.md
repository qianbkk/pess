---
name: clarify-prod
description: "Use after /clarify and before /plan. Triggers 5-step product review (value/priority/ROI/risk/alternatives), outputs Decision Card."
---

# /clarify-prod — 产品决策审查 (OPT-016)

> **触发条件**: 在 /clarify 之后, /plan 之前使用
> **目的**: 5 步产品审查, 输出 Decision Card
> **依赖**: spec.md 已存在

---

## 5 步产品审查

### 1. 用户价值
- 谁是用户？[目标用户画像]
- 他们为什么需要这个？[痛点]
- 价值主张：1 句话

### 2. 优先级
- 与现有功能的关系：[替代/补充/无关]
- MoSCoW：[Must/Should/Could/Won't]
- 不做会怎样？

### 3. ROI
- 投入：[开发工时估]
- 收益：[用户数 × 使用频次 × 价值/次]
- 投资回收期：[X 周/月]

### 4. 风险
- 技术风险：[列出 3 项]
- 市场风险：[列出 3 项]
- 合规风险：[GDPR/PII/...]

### 5. 替代方案
- 方案 A: [当前提议]
- 方案 B: [更轻量替代]
- 方案 C: [更重量替代]
- 推荐：[理由]

---

## Decision Card 输出

```
┌────────────────────────────────────┐
│ Decision Card: <feature-name>      │
├────────────────────────────────────┤
│ 价值:        [1 句话]              │
│ 优先级:      [Must/Should/Could]   │
│ ROI:         [回收期]              │
│ 风险:        [3 项]                │
│ 推荐方案:    [A/B/C]              │
│ 决策:        [待定/批准/拒绝]     │
└────────────────────────────────────┘
```

---

## 失败处理

- spec.md 不存在: 提示 "请先生成 spec (手动或 /specify 计划中)"
- 任何审查项用户回答 "跳过": 标记为未决定, 继续后续问题
