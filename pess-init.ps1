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
    # 替换项目名占位符
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

# 初始化 Memory Bank
Write-File (Join-Path $ProjectRoot "memory-bank/activeContext.md") @"
# 当前活跃上下文

更新时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm')

## 当前任务
正在实现: 项目初始化

## 刚完成
- [x] 项目结构创建

## 下一步
- [ ] 填写 CLAUDE.md 的技术栈和目录约定
- [ ] 填写 AGENTS.md 的 Build 命令
- [ ] 写第一个功能的 FEATURE_SPEC.md
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

# 从个人 Skills 库复制通用 Skills
$skillsSource = Join-Path $PessRoot "templates\skills"
$skillsDest = Join-Path $ProjectRoot ".claude/skills"
if (Test-Path $skillsSource) {
    Copy-Item "$skillsSource\security-patterns.md" $skillsDest -ErrorAction SilentlyContinue
    Copy-Item "$skillsSource\testing-patterns.md" $skillsDest -ErrorAction SilentlyContinue
    if ($ProjectType -eq "simulation") {
        Copy-Item "$skillsSource\simulation.md" $skillsDest -ErrorAction SilentlyContinue
    }
}

# 从个人 Commands 库复制通用 Commands
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
git commit -m "chore: init project with PESS v3.0" | Out-Null

Write-Host "`n✅ 项目 '$ProjectName' 已初始化" -ForegroundColor Green
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "  1. 填写 CLAUDE.md 的技术栈和目录约定" -ForegroundColor White
Write-Host "  2. 填写 AGENTS.md 的 Build 命令" -ForegroundColor White
Write-Host "  3. 用 /think 开始第一个功能" -ForegroundColor White