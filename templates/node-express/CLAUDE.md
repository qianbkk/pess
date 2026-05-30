# [PROJECT_NAME] 专属规范

## 技术栈（锁定版本）
- 运行时: Node.js 22
- 主框架: Express 4.x
- 测试: Jest 29
- 数据库: PostgreSQL 16 / MongoDB

## 目录约定（违反视为错误）
- API 路由: src/routes/        → 只做路由，不含业务逻辑
- 业务逻辑: src/services/      → 核心逻辑
- 数据访问: src/models/         → Mongoose 模型
- 测试: tests/                 → 镜像 src/ 结构

## 架构决策（禁止推翻，需修改先问我）
- 认证方案: JWT（jsonwebtoken）
- 数据库 ORM: Mongoose

## 项目专属禁令
- 禁止修改 src/core/ 下文件
- 禁止向 main 分支直接 push（必须通过 PR）

## 当前踩坑（已验证的规则）
- 统一使用 async/await，不使用 callbacks
- 环境变量用 dotenv，禁止硬编码