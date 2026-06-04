param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,

    [ValidateSet("python-fastapi", "node-express", "fullstack", "simulation", "default")]
    [string]$ProjectType = "default",

    [string]$Description = ""
)

$PessVersion = "3.3.1"
$PessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Join-Path (Get-Location) $ProjectName

function Create-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

function Write-File($path, $content) {
    $content | Set-Content -Path $path -Encoding UTF8
}

$dirs = @(".claude/commands", ".claude/skills", "memory-bank", "docs/spec", "docs/adr", "src", "tests")
foreach ($dir in $dirs) { Create-Dir (Join-Path $ProjectRoot $dir) }

$templatePath = Join-Path $PessRoot "templates\$ProjectType\CLAUDE.md"
$targetPath = Join-Path $ProjectRoot "CLAUDE.md"
if (Test-Path $templatePath) {
    Copy-Item $templatePath $targetPath
    $content = Get-Content $targetPath -Raw
    $content -replace '\[PROJECT_NAME\]', $ProjectName | Set-Content $targetPath -NoNewline
} else {
    Write-Warning "Template $templatePath not found"
    $content = "# $ProjectName`n`n## Tech Stack (to fill)`n`n## Conventions (to fill)`n"
    Set-Content -Path $targetPath -Value $content -Encoding UTF8
}

$agentsPath = Join-Path $ProjectRoot "AGENTS.md"
Set-Content -Path $agentsPath -Value @"
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
"@ -Encoding UTF8

$ts = Get-Date -Format 'yyyy-MM-dd HH:mm'

$activeCtx = @"
# Active Context

Updated: $ts

## Current Task
Implementing: Project initialization

## Done
- [x] Project structure created

## Next
- [ ] Fill CLAUDE.md (tech stack and conventions)
- [ ] Fill AGENTS.md Build commands
- [ ] Fill memory-bank/techContext.md
- [ ] Use /think to start first feature
"@
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\activeContext.md") -Value $activeCtx -Encoding UTF8

Set-Content -Path (Join-Path $ProjectRoot "memory-bank\systemPatterns.md") -Value "# System Patterns`n(TODO)`n" -Encoding UTF8
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\lessons.md") -Value "# Lessons Learned`n(Empty until you record a real mistake via /wrap)`n" -Encoding UTF8
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\session-notes.md") -Value "# Session Notes`n(Auto-written by /wrap, no manual maintenance needed)`n" -Encoding UTF8

$progress = @"
# Progress

Updated: $ts

## Completed
- [x] Project initialization

## Known Issues
(TODO)

## Next Milestone
(TODO)
"@
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\progress.md") -Value $progress -Encoding UTF8

$techCtx = @"
# Tech Context

Updated: $ts

## Tech Stack
- Language: (TODO, e.g. Python 3.12)
- Framework: (TODO, e.g. FastAPI 0.110)
- Database: (TODO)
- Test Tool: (TODO, e.g. pytest)
- Package Manager: (TODO, e.g. uv)

## Key Dependencies
(TODO)

## Dev Environment
- Run: (TODO)
- Test: (TODO)
- Lint: (TODO)

## Known Constraints
(TODO, e.g. Python 3.10 compatibility)
"@
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\techContext.md") -Value $techCtx -Encoding UTF8

$const = @"
# $ProjectName Constitution

> Project's supreme rules. All development must follow these principles.

## Non-Negotiable

### Quality底线
- Coverage: service >= 85%, API >= 70%
- No bare except/catch, must specify exception type

### Security红线
- No hardcoded secrets/tokens/keys
- All user input must be explicitly validated

### Project-Specific Constraints
(TODO)
"@
Set-Content -Path (Join-Path $ProjectRoot "memory-bank\constitution.md") -Value $const -Encoding UTF8

$skillsSrc = Join-Path $PessRoot "templates\skills"
$skillsDest = Join-Path $ProjectRoot ".claude\skills"
if (Test-Path $skillsSrc) {
    Copy-Item "$skillsSrc\security-patterns.md" $skillsDest -ErrorAction SilentlyContinue
    Copy-Item "$skillsSrc\testing-patterns.md" $skillsDest -ErrorAction SilentlyContinue
    if ($ProjectType -eq "simulation") {
        Copy-Item "$skillsSrc\simulation.md" $skillsDest -ErrorAction SilentlyContinue
    }
    # 注: ato-agent.md 不会通过 pess-init 自动复制 (OPT-002)
    # 它是项目专属 skill, 需要用户显式 cp 或 git pull
}

$cmdsSrc = Join-Path $PessRoot "templates\commands"
$cmdsDest = Join-Path $ProjectRoot ".claude\commands"
if (Test-Path $cmdsSrc) {
    Copy-Item "$cmdsSrc\*.md" $cmdsDest -ErrorAction SilentlyContinue
}

Set-Location $ProjectRoot
git init

$gitignore = @"
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
Set-Content -Path ".gitignore" -Value $gitignore -Encoding UTF8

git add -A
git commit -m "chore: init project with PESS v$PessVersion"

Write-Host ""
Write-Host "Project '$ProjectName' initialized (PESS v$PessVersion)" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Fill CLAUDE.md (tech stack and conventions)" -ForegroundColor White
Write-Host "  2. Fill AGENTS.md Build commands" -ForegroundColor White
Write-Host "  3. Fill memory-bank/techContext.md" -ForegroundColor White
Write-Host "  4. Fill memory-bank/constitution.md" -ForegroundColor White
Write-Host "  5. Use /think to start first feature" -ForegroundColor White
