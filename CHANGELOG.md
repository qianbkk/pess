# CHANGELOG

## v3.3.1 (2026-05-31)

### 修复
- `pess-update.ps1`: 版本检测改用 GitHub API，不再依赖本地 git 仓库（ZIP 安装用户也能正常使用）
- CI workflow: 测试框架动态检测（Vitest/Jest/Mocha/npm/Cargo/Go），失败时 exit 1 真正阻断

---

## v3.3.0 (2026-05-31)

### 修复
- `pess-install.ps1`: settings.json 自动合并 hooks，不再只打印警告（对已有 settings.json 的用户 hooks 真正生效）
- `pess-init.ps1`: 修复路径分隔符，全部改用 `Join-Path`
- `pess-init.sh`: 修复 SKILLS_SRC/SKILLS_DEST 变量未定义导致 Skills 复制失败的问题
- CI workflow: 区分 Vitest/Jest/Mocha 测试框架，测试失败正确 exit 1 阻断

### 新增
- `tests/test-init.ps1` — PESS 自测脚本，验证 pess-init 生成的项目结构完整
- `memory-bank/techContext.md` — Memory Bank 第6文件，技术栈/依赖/开发环境
- `/pess-adopt` 命令 — 存量项目渐进式引入 PESS 规范
- `memory-bank/lessons.md` 和 `progress.md` — 完善 6 文件体系

### 变更
- Memory Bank 升级为完整 6 文件体系
- `pess-init.ps1` / `pess-init.sh` commit message 更新为 v3.3

---

## v3.2.0 (2026-05-31)

### 新增
- CI/CD 集成：`templates/ci/github-actions/pess-quality.yml`
- `/doctor` 命令：`templates/commands/doctor.md`
- `pess-update.ps1` / `pess-update.sh`

### 跨平台
- 所有脚本提供双版本（.ps1 / .sh）

---

## v3.1.0 (2026-05-31)

### 新增
- Memory Bank 6 文件体系（progress.md、constitution.md）
- TDD 强制：testing-patterns 触发时机修正
- `/think` 红队挑战 + 范围确认
- `/plan` 任务ID + 复杂度 + 并行标记
- `/checkpoint` 结构化检查清单 + 覆盖率门控 + 回滚协议
- `/wrap` 自动更新 progress.md
- `/specify`（feature-spec.md 模板）
- Constitution + ADR 模板
- AGENTS.md RFC 2119 格式

---

## v3.0.0 (2026-05-30)

- 初始版本：5 命令 + 4 Skills + Hooks + Memory Bank + 项目模板