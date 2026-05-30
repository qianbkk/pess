# CHANGELOG

## v3.2.0 (2026-05-31)

### 新增
- CI/CD 集成：`templates/ci/github-actions/pess-quality.yml` — Memory Bank 结构验证、敏感信息扫描、绝对路径扫描、测试执行
- `/doctor` 命令：`templates/commands/doctor.md` — PESS 系统健康检查（Hooks 安装、项目初始化、Memory Bank 健康度）
- `pess-update.ps1` / `pess-update.sh` — 增量更新脚本，保留用户定制内容，支持 `--check` 检查更新

### 跨平台支持
- 所有脚本提供双版本：`.ps1`（Windows）+ `.sh`（macOS/Linux）

---

## v3.1.0 (2026-05-31)

### 新增
- Memory Bank 升级为 6 文件体系（新增 `progress.md`、`constitution.md`）
- TDD 强制执行：`testing-patterns` Skill 触发条件修正
- `/think` 增强：红队挑战 + 范围确认（In/Out/Deferred）
- `/plan` 增强：任务ID + 复杂度评分（S/M/L/XL）+ 并行标记
- `/checkpoint` 增强：结构化检查清单 + 覆盖率门控 + 回滚协议
- `/wrap` 增强：自动更新 `progress.md`
- `/specify`（feature-spec 模板）：`templates/commands/feature-spec.md`
- Constitution 模板：`templates/constitution.md`
- ADR 模板：`templates/adr-template.md`
- AGENTS.md 规范化：RFC 2119 MUST/SHOULD/MAY 格式

### 跨平台
- `pess-install.sh` / `pess-init.sh`（macOS/Linux）

---

## v3.0.0 (2026-05-30)

- 初始版本：5 命令 + 4 Skills + Hooks + Memory Bank + 项目模板