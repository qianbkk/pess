param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,

    [ValidateSet("python-fastapi", "node-express", "fullstack", "simulation", "default")]
    [string]$ProjectType = "default",

    [string]$Description = ""
)

$PessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Join-Path (Get-Location) $ProjectName

function Create-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

function Write-File($path, $content) {
    $content | Set-Content -Path $path -Encoding UTF8
}

# 创建目录结构
$dirs = @(
    ".claude/commands", ".claude/skills",
    "memory-bank", "docs/spec", "docs/adr",
    "src", "tests"
)
foreach ($dir in $dirs) { Create-Dir (Join-Path $ProjectRoot $dir) }

# 生成项目级 CLAUDE.md（从模板）
$templatePath = Join-Path $PessRoot "templates\$ProjectType\CLAUDE.md"
$targetPath = Join-Path $ProjectRoot "CLAUDE.md"
if (Test-Path $templatePath) {
    Copy-Item $templatePath $targetPath
    (Get-Content $targetPath) -replace '\[PROJECT_NAME\]', $ProjectName | Set-Content $targetPath
} else {
    Write-Warning "模板 $templatePath 不存在，使用默认模板"
    Write-File $targetPath "# $ProjectName 专属规范`n`n## 技术栈（待填写）`n`n## 目录约定（待填写）`n"
}

# 生成 AGENTS.md
Write-File (Join-Path $ProjectRoot "AGENTS.md") @"
# AGENTS.md

## Build
- Install: TODO
- Run: TODO
- Test: TODO
- Lint: TODO

## Constraints
- Branch: never push directly to main
- Secrets: never hardcode; always use environment variables

## Architecture
- Pattern: TODO
"@

# 初始化 Memory Bank — 6 文件体系
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'

Write-File (Join-Path $ProjectRoot "memory-bank/activeContext.md") @"
# 当前活跃上下文

更新时间: $timestamp

## 当前任务
正在实现: 项目初始化

## 刚完成
- [x] 项目结构创建

## 下一步
- [ ] 填写 CLAUDE.md 的技术栈和目录约定
- [ ] 填写 AGENTS.md 的 Build 命令
- [ ] 填写 memory-bank/techContext.md 的技术栈信息
- [ ] 用 /think 开始第一个功能
"@

Write-File (Join-Path $ProjectRoot "memory-bank/systemPatterns.md") @"
# 系统架构模式
（待填写）
"@

Write-File (Join-Path $ProjectRoot "memory-bank/lessons.md") @"
# 踩坑记录
（首次使用时此文件为空，遇到值得记录的问题后通过 /wrap 添加）
"@

Write-File (Join-Path $ProjectRoot "memory-bank/session-notes.md") @"
# 会话笔记（自动写入，无需手动维护）
"@

Write-File (Join-Path $ProjectRoot "memory-bank/progress.md") @"
# 项目进度

更新时间: $timestamp

## 已完成
- [x] 项目初始化

## 已知问题
（待解决的技术债或 bug）

## 下一里程碑
（待填写）
"@

Write-File (Join-Path $ProjectRoot "memory-bank/techContext.md") @"
# 技术上下文

更新时间: $timestamp

## 技术栈
- 语言：（待填写，例：Python 3.12）
- 框架：（待填写，例：FastAPI 0.110）
- 数据库：（待填写）
- 测试工具：（待填写，例：pytest）
- 包管理：（待填写，例：uv）

## 关键依赖
（待填写）

## 开发环境
- 运行命令：（待填写）
- 测试命令：（待填写）
- Lint 命令：（待填写）

## 已知约束
（待填写，例：Python 3.10 兼容性要求）
"@

Write-File (Join-Path $ProjectRoot "memory-bank/constitution.md") @"
# $ProjectName 项目宪法

> 这是项目的最高规范。所有后续开发必须遵守以下原则。

## 不可协商原则

### 质量底线
- 测试覆盖率: service 层 ≥ 85%，API 层 ≥ 70%
- 禁止裸 except/catch，必须指定异常类型

### 安全红线
- 禁止在代码中硬编码 secret/token/key
- 所有用户输入必须经过显式验证

### 项目特定约束
（待填写）
"@

# 复制 Skills（通用 + simulation 类型专用）
$skillsSource = Join-Path $PessRoot "templates\skills"
$skillsDest = Join-Path $ProjectRoot ".claude/skills"
if (Test-Path $skillsSource) {
    Copy-Item "$skillsSource\security-patterns.md" $skillsDest -ErrorAction SilentlyContinue
    Copy-Item "$skillsSource\testing-patterns.md"  $skillsDest -ErrorAction SilentlyContinue
    if ($ProjectType -eq "simulation") {
        Copy-Item "$skillsSource\simulation.md" $skillsDest -ErrorAction SilentlyContinue
    }
}

# 复制 Commands
$cmdsSource = Join-Path $PessRoot "templates\commands"
$cmdsDest = Join-Path $ProjectRoot ".claude/commands"
if (Test-Path $cmdsSource) {
    Copy-Item "$cmdsSource\*.md" $cmdsDest -ErrorAction SilentlyContinue
}

# 初始化 git
Set-Location $ProjectRoot
git init | Out-Null
Write-File ".gitignore" @"
.env
.env.*
*.pem
*.key
__pycache__/
*.pyc
node_modules/
dist/
.DS_Store
"@

git add -A | Out-Null
git commit -m "chore: init project with PESS v3.3" | Out-Null

Write-Host "`n项目 '$ProjectName' 已初始化 (PESS v3.3)" -ForegroundColor Green
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "  1. 填写 CLAUDE.md 的技术栈和目录约定" -ForegroundColor White
Write-Host "  2. 填写 AGENTS.md 的 Build 命令" -ForegroundColor White
Write-Host "  3. 填写 memory-bank/techContext.md" -ForegroundColor White
Write-Host "  4. 填写 memory-bank/constitution.md" -ForegroundColor White
Write-Host "  5. 用 /think 开始第一个功能" -ForegroundColor White