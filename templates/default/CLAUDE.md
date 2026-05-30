# [PROJECT_NAME] 专属规范

## 技术栈（锁定版本）
- 运行时: Python 3.12
- 主框架: FastAPI 0.115
- 测试: pytest 8.x
- 数据库: PostgreSQL 16 / SQLite

## 目录约定（违反视为错误）
- API 路由: src/api/          → 只做参数验证，不含业务逻辑
- 业务逻辑: src/services/      → 核心逻辑
- 数据访问: src/repositories/  → 禁止在 services 层写 SQL
- 测试: tests/                 → 镜像 src/ 结构

## 架构决策（禁止推翻，需修改先问我）
- 认证方案: JWT
- 数据库 ORM: SQLAlchemy

## 项目专属禁令
- 禁止修改 src/core/ 下文件（需说"修改核心"才解锁）
- 禁止向 main 分支直接 push（必须通过 PR）

## 当前踩坑（已验证的规则）
- 分页参数统一用 page/page_size，不用 page_number
- Redis Key 格式: "namespace:type:id"，不能随意命名