# /checkpoint — 质量门控与检查点提交

按顺序执行，每步失败时停下来报告，不要跳过：

## Checkpoint Checklist

- [ ] 代码通过 lint（ruff / eslint）
- [ ] 核心路径有测试覆盖
- [ ] 无硬编码 secret 或绝对路径
- [ ] Memory Bank 已更新（如有架构变化）
- [ ] 变更内容在计划中的任务 ID 已标记完成

---

**第一步：静态检查**
```bash
# Python 项目
ruff check src/ --fix
mypy src/ --ignore-missing-imports

# JS/TS 项目
npm run lint -- --fix
npm run typecheck
```

**第二步：运行测试**
```bash
# Python
pytest tests/ -v --tb=short

# JS/TS
npm test -- --run
```

**第三步：覆盖率检查（如项目配置了覆盖率）**
```bash
pytest --cov=src --cov-report=term-missing
# 门控：service 层 ≥ 85%，API 层 ≥ 70%
```

**第四步：提交（仅前三步全部通过后）**
```bash
git add -A
git diff --staged --stat
```
输出变更摘要，等待确认后：
```bash
git commit -m "[确认的信息]"
```

**第五步：更新 progress.md**
在 progress.md 的"已完成"区块追加一行：
```
- [日期] [任务ID] [一句话描述]
```

---

**回滚协议（如第二步失败）**：
- `git stash` 当前修改
- 记录失败的测试名称
- 输出修复建议
- 等待我指示，不自动回退