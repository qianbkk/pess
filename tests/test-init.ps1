# tests/test-init.ps1 — PESS 初始化脚本的基础验证
$ErrorCount = 0
$PessRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Assert($condition, $message) {
    if ($condition) {
        Write-Host "  PASS  $message" -ForegroundColor Green
    } else {
        Write-Host "  FAIL  $message" -ForegroundColor Red
        $script:ErrorCount++
    }
}

# 在临时目录运行 pess-init
$TempDir = Join-Path $env:TEMP "pess-test-$(Get-Random)"
New-Item -ItemType Directory -Path $TempDir | Out-Null
Push-Location $TempDir

& "$PessRoot\pess-init.ps1" -ProjectName "test-project" -ProjectType "default" | Out-Null

$proj = Join-Path $TempDir "test-project"

Write-Host "`n--- 目录结构 ---"
Assert (Test-Path "$proj\.claude\commands")    ".claude/commands 存在"
Assert (Test-Path "$proj\.claude\skills")      ".claude/skills 存在"
Assert (Test-Path "$proj\memory-bank")           "memory-bank 存在"
Assert (Test-Path "$proj\docs\spec")            "docs/spec 存在"
Assert (Test-Path "$proj\docs\adr")             "docs/adr 存在"
Assert (Test-Path "$proj\src")                  "src 存在"
Assert (Test-Path "$proj\tests")                "tests 存在"

Write-Host "`n--- 核心文件 ---"
Assert (Test-Path "$proj\CLAUDE.md")                           "CLAUDE.md 已生成"
Assert (Test-Path "$proj\AGENTS.md")                           "AGENTS.md 已生成"
Assert (Test-Path "$proj\memory-bank\activeContext.md")        "activeContext.md 存在"
Assert (Test-Path "$proj\memory-bank\systemPatterns.md")       "systemPatterns.md 存在"
Assert (Test-Path "$proj\memory-bank\lessons.md")              "lessons.md 存在"
Assert (Test-Path "$proj\memory-bank\session-notes.md")        "session-notes.md 存在"
Assert (Test-Path "$proj\memory-bank\progress.md")             "progress.md 存在"
Assert (Test-Path "$proj\memory-bank\constitution.md")        "constitution.md 存在"

Write-Host "`n--- 内容验证 ---"
$claude = Get-Content "$proj\CLAUDE.md" -Raw
Assert ($claude -notmatch '\[PROJECT_NAME\]')  "CLAUDE.md 中占位符已替换"
Assert ($claude -match 'test-project')         "CLAUDE.md 包含项目名"

$const = Get-Content "$proj\memory-bank\constitution.md" -Raw
Assert ($const -match 'test-project')          "constitution.md 包含项目名"

Write-Host "`n--- Commands 和 Skills ---"
Assert ((Get-ChildItem "$proj\.claude\commands" -File).Count -ge 5)  "Commands >= 5 个文件"
Assert (Test-Path "$proj\.claude\skills\security-patterns.md")    "security-patterns.md 已复制"
Assert (Test-Path "$proj\.claude\skills\testing-patterns.md")     "testing-patterns.md 已复制"

Write-Host "`n--- Git ---"
Assert (Test-Path "$proj\.git")       "git 已初始化"
Assert (Test-Path "$proj\.gitignore")  ".gitignore 存在"

Pop-Location
Remove-Item $TempDir -Recurse -Force

Write-Host "`n=============================="
if ($ErrorCount -eq 0) {
    Write-Host "全部测试通过" -ForegroundColor Green
} else {
    Write-Host "$ErrorCount 项测试失败" -ForegroundColor Red
    exit 1
}