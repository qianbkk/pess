---
name: security-patterns
description: "当代码涉及用户认证、JWT、OAuth、API 密钥、密码哈希、HTTP 端点、会话管理、文件上传、SQL 查询或任何用户输入处理时自动加载。"
---

## 安全实现规范

### 认证与授权
- JWT：使用 PyJWT/jose，必须验证 exp/iss/aud，禁止 alg=none
- 密码哈希：bcrypt（cost≥12）或 argon2，禁止 MD5/SHA1
- API 密钥：存环境变量，传输走 Authorization header，禁止 URL 参数
- 会话：HttpOnly + Secure + SameSite=Strict Cookie

### 输入验证
- 所有外部输入必须用 Pydantic/zod 声明式验证
- 文件上传：白名单 MIME 类型 + 大小限制 + 随机重命名
- SQL：只用参数化查询（`?` 占位符），禁止字符串拼接

### 常见安全反模式（遇到立即标记）
- `eval()` / `exec()` 处理用户输入 → 立即标记为阻断性漏洞
- 日志中输出密码/token/密钥 → 立即标记
- `shell=True` 执行含用户输入的命令 → 立即标记
- 不验证 redirect_uri 的 OAuth → 立即标记
- 异常后返回详细错误栈给客户端 → 立即标记

### 审计日志（涉及敏感操作时）
- 记录所有认证事件（成功/失败）
- 记录所有权限变更
- 不记录敏感数据（密码、token 内容）