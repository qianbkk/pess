# tests/test-init.ps1 — PESS self-test
$ErrorCount = 0
$PessRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Assert($condition, $message) {
    if ($condition) {
        Write-Host "  PASS  " -NoNewline -ForegroundColor Green
        Write-Host $message
    } else {
        Write-Host "  FAIL  " -NoNewline -ForegroundColor Red
        Write-Host $message
        $script:ErrorCount++
    }
}

$TempDir = Join-Path $env:TEMP "pess-test-$(Get-Random)"
New-Item -ItemType Directory -Path $TempDir | Out-Null
Push-Location $TempDir

& "$PessRoot\pess-init.ps1" -ProjectName "test-proj" -ProjectType "default" | Out-Null
$proj = Join-Path $TempDir "test-proj"

Write-Host ""
Write-Host "--- Directory Structure ---"
Assert (Test-Path "$proj\.claude\commands")    ".claude/commands exists"
Assert (Test-Path "$proj\.claude\skills")     ".claude/skills exists"
Assert (Test-Path "$proj\memory-bank")         "memory-bank exists"
Assert (Test-Path "$proj\docs\spec")         "docs/spec exists"
Assert (Test-Path "$proj\docs\adr")          "docs/adr exists"
Assert (Test-Path "$proj\src")                "src exists"
Assert (Test-Path "$proj\tests")               "tests exists"

Write-Host ""
Write-Host "--- Core Files ---"
Assert (Test-Path "$proj\CLAUDE.md")                            "CLAUDE.md generated"
Assert (Test-Path "$proj\AGENTS.md")                            "AGENTS.md generated"
Assert (Test-Path "$proj\memory-bank\activeContext.md")         "activeContext.md exists"
Assert (Test-Path "$proj\memory-bank\systemPatterns.md")        "systemPatterns.md exists"
Assert (Test-Path "$proj\memory-bank\lessons.md")               "lessons.md exists"
Assert (Test-Path "$proj\memory-bank\session-notes.md")         "session-notes.md exists"
Assert (Test-Path "$proj\memory-bank\progress.md")              "progress.md exists"
Assert (Test-Path "$proj\memory-bank\constitution.md")          "constitution.md exists"
Assert (Test-Path "$proj\memory-bank\techContext.md")          "techContext.md exists"

Write-Host ""
Write-Host "--- Content Validation ---"
$claude = Get-Content "$proj\CLAUDE.md" -Raw
Assert ($claude -notmatch '\[PROJECT_NAME\]')  "CLAUDE.md placeholder replaced"
Assert ($claude -match 'test-proj')              "CLAUDE.md contains project name"

$const = Get-Content "$proj\memory-bank\constitution.md" -Raw
Assert ($const -match 'test-proj')               "constitution.md contains project name"

Write-Host ""
Write-Host "--- Commands and Skills ---"
Assert ((Get-ChildItem "$proj\.claude\commands" -File).Count -ge 5)  "Commands >= 5 files"
Assert (Test-Path "$proj\.claude\skills\security-patterns.md")    "security-patterns.md copied"
Assert (Test-Path "$proj\.claude\skills\testing-patterns.md")     "testing-patterns.md copied"

Write-Host ""
Write-Host "=============================="
if ($ErrorCount -eq 0) {
    Write-Host "All tests passed" -ForegroundColor Green
} else {
    Write-Host "$ErrorCount tests failed" -ForegroundColor Red
    exit 1
}

Pop-Location
Remove-Item $TempDir -Recurse -Force
