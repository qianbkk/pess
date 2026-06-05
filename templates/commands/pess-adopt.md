---
name: pess-adopt
description: "Use when user is adding PESS to an existing project. Triggers 5-stage incremental adoption guide. Do not load for greenfield projects (use pess-init)."
---

# /pess-adopt — 为已有项目引入 PESS 规范（存量项目适配）

> 适用场景：一个已有代码库，想要引入 PESS 规范但不想重建项目。

---

## 第一步：扫描现有项目

检测项目类型和技术栈：

```bash
# 检测语言和框架
ls *.py *.ts *.js 2>/dev/null | head -5
cat package.json pyproject.toml setup.py Gemfile Cargo.toml 2>/dev/null

# 检测测试框架
ls tests/ test/ __tests__/ 2>/dev/null
cat pytest.ini jest.config.* vitest.config.* 2>/dev/null

# 检测 lint 配置
cat .eslintrc .pylintrc ruff.toml .rubocop.yml 2>/dev/null

# 检测 CI
ls .github/workflows/ .gitlab-ci.yml 2>/dev/null
```

---

## 第二步：生成初始 CLAUDE.md

基于扫描结果，生成项目专属规范：

```
技术栈：[检测到的语言/框架]
测试框架：[检测到的测试工具]
包管理器：[检测到的包管理]
CI：[检测到的 CI 系统]

目录约定：
  - [列出主要目录结构]

架构决策：
  - [从代码中识别的架构模式]
```

---

## 第三步：初始化 Memory Bank（渐进式）

可以选择只启用部分组件：

### 只启用 Commands
```bash
mkdir -p .claude/commands
cp PESS_ROOT/templates/commands/*.md .claude/commands/
```

### 只启用 Memory Bank
```bash
mkdir -p memory-bank
# 初始化 6 文件，但不强制填写
```

### 启用全部
```bash
# 运行完整的 pess-init（但跳过 git init）
./PESS_ROOT/pess-init.sh -n [项目名] --skip-git
```

---

## 第四步：创建初始规格记录

在 `docs/changes/` 目录中记录当前状态：

```
docs/changes/
└── YYYY-MM-DD-initial-adoption.md
    - 已检测技术栈：...
    - 已启用组件：...
    - 未启用组件：...
    - 初始架构决策：...
```

---

## 渐进式启用建议

| 优先级 | 组件 | 理由 |
|--------|------|------|
| 1 | `/checkpoint` | 最快见效，强制提交规范 |
| 2 | Memory Bank | 跨会话上下文积累 |
| 3 | `/think` | 重大功能前强制思考 |
| 4 | `/review` | PR 前多维审查 |
| 5 | `/plan` | 复杂任务结构化 |

不要一次性启用全部命令——选择一个最痛的地方开始。