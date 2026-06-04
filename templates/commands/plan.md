# /plan — 任务分解 + 强制 TDD (OPT-017 升级)

> **触发条件**: spec 已确定方向后, /change propose 之前使用
> **依赖**: /clarify-prod 或 /clarify-arch 推荐 (不强制)

---

## 输出格式（每个 T-N 必含 Test First）

```markdown
# Plan: <feature-name>

## 任务分解

### T-001 [S] 数据模型设计
- [Test] 写 test_models.py: 验证 User/Post/Comment schema
- [Impl] 实现 SQLAlchemy models
- [Verify] `pytest tests/test_models.py -v`

### T-002 [M] API endpoint 实现
- [Test] 写 test_api.py: 验证 GET/POST/PUT/DELETE
- [Impl] FastAPI routes
- [Verify] `pytest tests/test_api.py -v` + 集成测试

### T-003 [L] 性能回归检查
- [Test] 写 bench_api.py: locust 压测
- [Impl] 加缓存层
- [Verify] P99 < 200ms

## 验收标准
- [ ] 所有 T-N 的 Test First 子任务完成
- [ ] coverage ≥ 80%
- [ ] constitution.md 红线 0 突破
```

---

## 与 testing-patterns skill 联动

- description 包含 "TDD skill auto-loaded" 提示
- AI 自动加载 testing-patterns skill
- 每个 T-N 强制含 [Test] 子任务（无 [Test] 的 T-N 被 plan 拒绝）

---

## 并行标记

- 同一波次的 T-N 可并行
- 不同波次依赖关系显式标注
