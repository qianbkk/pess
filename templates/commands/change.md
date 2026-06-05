---
name: change
description: "Use when user wants to track a feature as a formal change with status machine (PROPOSED → APPLYING → TESTING → ARCHIVED). Triggers one of three subcommands: propose, apply, archive."
---

# /change — 功能变更命令族 (OPT-009)

> **3 个子命令**: propose → apply → archive
> **状态机**: PROPOSED → APPLYING → TESTING → ARCHIVED
> **依赖**: docs/adr/ 或 docs/spec/ 已存在 (用 features/<id>/ 子目录管理)

---

## 子命令 1: `/change propose <描述>`

**目的**: 写变更提案到 `docs/changes/<feature-id>/proposal.md`

### 步骤

1. **生成 feature-id**: `CHG-YYYYMMDD-HHmm` (例: `CHG-20260605-1430`)
2. **创建目录**: `docs/changes/<feature-id>/`
3. **写 proposal.md** (模板见下方)
4. **初始化 STATUS.md** (项目根):
   - 追加 `## <feature-id>` 段到 STATUS.md
   - 状态: PROPOSED
5. **git commit**: `chore: propose change <feature-id>`

### proposal.md 模板

```markdown
# Change Proposal: <feature-id>

> 状态: PROPOSED | 创建: <timestamp> | 作者: <user>

## 1. 问题陈述
[为什么要做这个变更？1-2 段]

## 2. 提议方案
[高层设计, 2-3 段, 不写代码细节]

## 3. 影响的范围
- 模块: [src/, tests/, docs/...]
- 兼容性: [向后兼容 / 破坏性]
- 风险: [列出]

## 4. 验收标准
- [ ] AC-1: [可测量的验收条件]
- [ ] AC-2: [...]
- [ ] AC-3: [...]

## 5. 任务分解 (粗略)
- T-1 [S]: ...
- T-2 [M]: ...
- T-3 [L]: ...
```

---

## 子命令 2: `/change apply <feature-id>`

**目的**: 把 PROPOSED 状态推进到 APPLYING，开始实施

### 步骤

1. 读取 `docs/changes/<feature-id>/proposal.md` 验证存在
2. 更新 STATUS.md: `PROPOSED → APPLYING`
3. 在 proposal.md 末尾追加 "## Implementation Notes" 段（实施时填写）
4. 输出 "✅ <feature-id> 进入 APPLYING, 开始实施"
5. **不自动执行任何代码改动** — 这是用户的工作

---

## 子命令 3: `/change archive <feature-id>`

**目的**: 完成实施，归档到 progress.md

### 步骤

1. 读取 `docs/changes/<feature-id>/proposal.md`
2. 验证所有 AC 已完成（询问用户或扫描 git log）
3. 更新 STATUS.md: `APPLYING → TESTING → ARCHIVED`
4. 追加到 `memory-bank/progress.md`:
   ```markdown
   ## [YYYY-MM-DD] <feature-id> 归档
   - 解决了: [简述]
   - 关键决策: [链接到 ADR 如果有]
   - 任务数: N (完成 M)
   - 经验: [踩坑或亮点]
   ```
5. 移动 proposal.md 到 `docs/changes/.archive/<feature-id>/`
6. git commit: `chore: archive change <feature-id>`

---

## STATUS.md schema

项目根的 STATUS.md 维护所有活跃变更：

```markdown
# Project Status Board

> 跨会话的共享黑板. 由 /change 和 /wrap 自动维护.

## Active Features

### CHG-20260605-1430 (PROPOSED)
- Title: 优化 todo API 性能
- Proposal: docs/changes/CHG-20260605-1430/proposal.md
- Progress: 0/3 AC done
- Risks: 数据迁移

## Recently Archived
- CHG-20260528-0915 (ARCHIVED): [链接]

## Recently Adopted
- (新项目 / 新 spec 引入时记录)

## Cross-Feature Notes
- 跨多个 feature 的共性约束
```

---

## 与 /wrap 的协同

- `/wrap` 会**只读**扫描 STATUS.md 统计活跃 feature 数
- `/wrap` 不会修改 STATUS.md (避免状态漂移)
- 任何状态推进必须通过 `/change` 子命令

---

## 错误处理

- **feature-id 不存在**: 提示可用 feature-id 列表
- **状态非法跳转** (e.g. PROPOSED → ARCHIVED 跳过 APPLYING): 拒绝并提示
- **apply 时 proposal.md 不存在**: 拒绝并提示先 propose
