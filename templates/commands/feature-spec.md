---
name: feature-spec
description: "Template for feature specifications. Used by /specify command (not a command itself). Do not invoke directly."
---

# Feature Spec: [功能名称]

## Overview
**背景**: [为什么需要这个功能]
**目标**: [具体可测量的目标]
**相关 issue/讨论**: [链接，如有]

---

## User Stories

| As a... | I want... | So that... | Acceptance Criteria |
|---------|-----------|-----------|---------------------|
| [用户类型] | [功能描述] | [期望结果] | [可验证标准] |

---

## Technical Design

### 影响范围
- **修改文件**: [列表]
- **新建文件**: [列表]
- **不影响**: [明确排除的文件]

### 核心逻辑
[简述实现方案，精确到模块/函数/接口级别]

### 数据模型
[数据变更时填写：新增表/字段、Schema 变更]

### API 设计
[涉及 API 时填写]
- Endpoint:
- Method:
- Request:
- Response:

---

## Task List

| ID | 任务 | 复杂度 | 验证标准 | 状态 |
|----|------|--------|----------|------|
| T-001 | [描述] | S/M/L/XL | [完成标志] | TODO |
| T-002 | [描述] | S/M/L/XL | [完成标志] | TODO |

**依赖关系**: T-002 依赖 T-001

---

## Test Strategy

| 层次 | 测试什么 | 测试方式 |
|------|----------|----------|
| 单元 | [函数/方法] | [描述] |
| 集成 | [接口/流程] | [描述] |
| E2E | [用户路径] | [描述] |

---

## Out of Scope
- [明确不包含的内容]

---

## Open Questions
- [尚未确定的问题]

---

*创建时间: [YYYY-MM-DD] | 状态: DRAFT*