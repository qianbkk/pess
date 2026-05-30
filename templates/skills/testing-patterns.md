---
name: testing-patterns
description: "当创建或修改测试文件（test_*.py、*.test.ts、*.spec.ts）时自动加载。提供测试组织规范、Mock 策略和覆盖率要求。不适用于非测试文件。"
---

## 测试规范

### 测试组织
- 测试文件位置：tests/ 目录，镜像 src/ 结构
- 命名：test_{module}.py 对应 src/{module}.py
- 每个测试函数名必须描述被测场景：test_{function}_{scenario}_{expected}

### 测试分层策略
- 单元测试：所有 service 层函数必须覆盖（Mock 外部依赖）
- 集成测试：所有 API 端点必须覆盖（使用 TestClient/supertest）
- 不要对 repository 层写大量 Mock，优先用 SQLite 内存数据库

### Fixture 规范
- 数据库 Fixture：tests/conftest.py 中定义，函数级 scope
- 工厂：tests/factories/ 目录，使用 factory_boy 或 @factory 装饰器
- 禁止在测试文件中硬编码测试数据，必须通过 Fixture

### 覆盖率要求
- service 层：≥85%
- api 层：≥70%
- core 层（基础设施）：≥60%
- 运行：`pytest --cov=src --cov-report=term-missing`