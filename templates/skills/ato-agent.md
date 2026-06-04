---
name: ato-context
description: "ONLY load when user explicitly references ATO (Agent Team Orchestrator) multi-agent orchestration. Do NOT auto-load for general FastAPI/Vite/React work — those have many non-ATO projects. ATO requires dispatcher XML, 15s polling, and specific port allocations documented below."
---

## ATO 项目锁定规范

### 核心锁定决策（禁止推翻，需修改先问我）
- Dispatch 协议：`<ato-dispatch>` XML 格式，字段顺序固定
- 轮询间隔：15 秒（已调试确认，不得随意修改）
- 超时阈值：120 秒
- Agent 通信：每次消息独立 CLI 调用，不维护长连接
- Windows Agent 启动：PowerShell `Start-Process`，禁止使用 psmux

### 接口规范
- 后端：FastAPI，端口 8000
- 前端：Vite/React，端口 5173
- API 前缀：统一 `/api/v1/`
- 参考实现：src/coordinator/dispatch.py（协调器核心）

### Windows 兼容性约束
- 所有路径操作使用 `pathlib.Path`
- 进程管理使用 `subprocess`，不依赖 Unix 特有工具