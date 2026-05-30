# [PROJECT_NAME] 专属规范

## 技术栈（锁定版本）
- 运行时: Python 3.12
- 主框架: FastAPI 0.115
- 测试: pytest 8.x, pytest-asyncio
- 数据库: PostgreSQL 16
- ORM: SQLAlchemy 2.0
- 验证: Pydantic v2

## 目录约定（违反视为错误）
- API 路由: src/api/          → 只做参数验证，不含业务逻辑
- 业务逻辑: src/services/      → 核心逻辑
- 数据访问: src/repositories/  → 禁止在 services 层写 SQL
- 领域模型: src/models/       → Pydantic 模型
- 测试: tests/                 → 镜像 src/ 结构

## API 设计规范
- 统一前缀: /api/v1/
- 响应格式: {data, error, meta}
- 错误码: 1000-1999 客户端错误，2000-2999 服务端错误

## 架构决策（禁止推翻，需修改先问我）
- 认证方案: JWT（PyJWT）
- 数据库 ORM: SQLAlchemy 2.0 with async
- 缓存: Redis

## 项目专属禁令
- 禁止修改 src/core/ 下文件（需说"修改核心"才解锁）
- 禁止向 main 分支直接 push（必须通过 PR）
- 禁止在 API 层直接操作数据库，必须通过 services

## 当前踩坑（已验证的规则）
- 分页参数统一用 page/page_size，不用 page_number
- Redis Key 格式: "namespace:type:id"
- 所有时间用 UTC，存储用 ISO 格式