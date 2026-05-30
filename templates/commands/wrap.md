# /wrap — 会话收尾

**第一步：自动写入（始终执行，无需确认）**
向 memory-bank/session-notes.md 末尾追加：
```
时间: [当前时间]
任务: [一句话]
完成: [bullet list]
未完成: [bullet list，如有]
```

**第二步：更新 progress.md**
在 progress.md 的"已完成"或"已知问题"区块追加对应内容。

**第三步：生成草稿（输出给我审核，不自动写入）**
a) activeContext.md 更新草稿

b) lessons.md 新增条目草稿（如有值得记录的问题）
```
- [日期] [问题描述] → [解决方案]
```

**第四步：等待我的指令**
- 说"更新上下文"→ 写入 activeContext.md
- 说"记录教训"→ 追加到 lessons.md
- 说"两个都要"→ 两个都写入
- 说"跳过"→ 只保留自动记录

这样设计：即使你最累的时候直接关闭会话，session-notes.md 和 progress.md 的记录也已经完成。