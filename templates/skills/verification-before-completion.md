---
name: verification-before-completion
description: "Load when AI is about to claim task completion. Do not load during code writing — only at the 'I'm done' checkpoint. Enforces 5-step verification gate before AI can say 'completed'."
---

# 完成前验证 (verification-before-completion skill, OPT-010)

> **核心反模式**: "应该没问题" / "看起来对了" / "理论上能跑"

---

## 触发条件

AI 输出含以下任一信号时**必须**加载本 skill：
- "完成" / "完成" / "已实现"
- "搞定" / "done" / "finished"
- "可以 merge 了" / "ready to ship"

---

## 5 步验证 Gate

### Gate 1: 跑测试
- [ ] 单元测试: `pytest tests/ -v` 或 `npm test`
- [ ] 集成测试: 端到端跑一遍
- [ ] 输出真存在 (不是"已运行"但实际没跑)

### Gate 2: 看输出
- [ ] 测试输出文件实际生成
- [ ] 数字、统计、日志匹配预期
- [ ] 没有被静默 except 吞掉的错误

### Gate 3: 验证不变量
- [ ] 核心假设仍成立 (e.g. 类型不变、API 兼容)
- [ ] 没有破坏其他模块
- [ ] 边界条件都覆盖 (空、None、超大、并发)

### Gate 4: 反思失败模式
- [ ] "如果这个错了, 错在哪里?"
- [ ] "我有没有忽略什么信号?"
- [ ] "其他工程师会怎么 review 这段?"

### Gate 5: 显式确认
- [ ] 输出明确的 "✅ 完成, 已通过 Gate 1-5"
- [ ] 不含 "应该" / "可能" / "应该" 模糊词
- [ ] 列出实际跑了什么命令 + 输出

---

## 反模式清单 (禁止使用)

| 反模式 | 后果 |
|--------|------|
| "应该没问题" | 隐藏未测假设 |
| "看起来对了" | 主观判断代替验证 |
| "理论上能跑" | 理论与实践脱节 |
| "跑了一下, 没报错" | 没看实际输出 |
| "类似功能之前能跑" | 没在当前代码上验证 |

---

## 与 using-pess 协同

- using-pess 提供"何时用什么命令"
- verification-before-completion 提供"声称完成时必走 5 步"
- 两者结合 = PESS 完整工作流纪律

---

## 失败处理

| 失败 | 动作 |
|------|------|
| Gate 1 测试失败 | 修复后再声称完成 |
| Gate 3 不变量破坏 | 回滚到上一个 git 标签 |
| Gate 5 显式确认缺失 | 强制重写完成声明 |
