---
name: careful
description: "Use when user inputs a destructive bash command (rm -rf, DROP TABLE, write to /dev/sda). Triggers second-confirmation flow. Do not load for read-only commands."
---

# /careful — 危险命令二次确认 (OPT-015)

> **触发条件**: 用户输入 /careful 后跟命令, 或 hook 拦截到危险命令时
> **行为**: 拦截危险命令 + 强制 AI 输出完整命令+影响给用户二次确认

---

## 工作流程

### 1. 拦截判定
通过 `guard_commands.py` 已有的 3 条 HARD_BLOCK_RE 模式识别：
- `rm -rf /` / `rm -rf ~` 
- `DROP TABLE` / `DROP DATABASE`
- `> /dev/sda` / `> /dev/nvme0`

### 2. 二次确认输出格式

当 hook 触发后，AI 必须按以下格式输出：

```
⚠️  危险命令已拦截 (二次确认请求):

```bash
[完整命令原文]
```

潜在影响:
- [影响 1: 例如删除 / 下所有文件, 系统将无法启动]
- [影响 2: ...]

如需执行, 请在下一轮回复中明确说:
  '强制执行: <完整命令>'

⚠️  不要直接重试此命令, 这会再次被拦截
```

### 3. 用户确认

- 用户说"强制执行: <命令>" → 解除拦截, 命令继续
- 用户说"取消" → 不执行
- 用户说其他 → 继续询问意图

---

## 与 /freeze 的区别

| 维度 | /careful | /freeze |
|------|----------|---------|
| 对象 | 单次命令 | 整个目录 |
| 解除 | 显式说"强制执行" | /unfreeze <path> |
| 强度 | 单次拦截 | 持续拦截直到解冻 |
