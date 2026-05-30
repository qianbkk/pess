# /checkpoint — 质量门控与检查点提交

按顺序执行，每步失败时停下来报告，不要跳过：

**第一步：静态检查**
```bash
# Python 项目
ruff check src/ --fix
mypy src/ --ignore-missing-imports

# JS/TS 项目
npm run lint -- --fix
npm run typecheck
```

**第二步：测试**
```bash
# Python
pytest tests/ -v --tb=short

# JS/TS
npm test -- --run
```

如果有测试失败：
- 列出失败的测试名称
- 输出失败原因（不超过5行）
- 停止，等待我指示

**第三步：提交（仅在前两步全部通过后）**
```bash
git add -A
git diff --staged --stat
```
输出变更摘要，等待我确认提交信息，然后：
```bash
git commit -m "[我确认的信息]"
```

**第四步：更新进度**
在 session-notes.md 末尾追加一行：
```
[时间] ✅ checkpoint: [一句话描述完成的内容]
```