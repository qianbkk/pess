# [PROJECT_NAME] 专属规范

## 技术栈（锁定版本）
- 前端: Vite + React 19 + TypeScript
- 后端: FastAPI (Python) + PostgreSQL
- 测试: Vitest (前端) + pytest (后端)

## 目录约定（违反视为错误）
- 前端: frontend/src/         → React 组件
- 后端: backend/src/          → FastAPI 路由和服务
- 共享: packages/shared/       → 类型定义和工具函数

## API 设计规范
- RESTful 风格
- 统一前缀: /api/v1/
- 前后端通过 OpenAPI 规范共享类型

## 架构决策（禁止推翻，需修改先问我）
- 前后端分离：通过 REST API 通信
- 数据库 ORM: SQLAlchemy 2.0

## 项目专属禁令
- 禁止在前端代码中直接调用数据库
- 禁止在后端代码中直接操作前端状态
- 禁止向 main 分支直接 push（必须通过 PR）