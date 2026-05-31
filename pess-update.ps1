# pess-update.ps1 — Update PESS to latest version (Windows)
# Usage: .\pess-update.ps1 [-CheckOnly]

param(
    [switch]$CheckOnly
)

$CURRENT_VERSION = "3.3.0"
$UPDATE_BASE = "https://github.com/qianbkk/pess.git"
$API_URL = "https://api.github.com/repos/qianbkk/pess/releases/latest"

Write-Host "PESS Updater v$CURRENT_VERSION" -ForegroundColor Cyan

function Get-LatestTag {
    try {
        $response = Invoke-RestMethod $API_URL -Headers @{Accept="application/vnd.github+json"} -TimeoutSec 10
        return $response.tag_name -replace 'v', ''
    } catch {
        return $null
    }
}

if ($CheckOnly) {
    Write-Host "Checking for updates..."
    $latestTag = Get-LatestTag
    if ($null -eq $latestTag) { $latestTag = $CURRENT_VERSION }
    if ($latestTag -eq $CURRENT_VERSION) {
        Write-Host "You are on the latest version: v$CURRENT_VERSION" -ForegroundColor Green
    } else {
        Write-Host "New version available: v$latestTag (you have v$CURRENT_VERSION)" -ForegroundColor Yellow
    }
    return
}

Write-Host "Fetching latest version from GitHub..." -ForegroundColor Cyan

# Preserve existing user hooks
$localHooks = "$env:USERPROFILE\.claude\hooks"
if (Test-Path $localHooks) {
    Write-Host "Preserving existing hooks in $localHooks" -ForegroundColor Yellow
}

# Add upstream remote and fetch
git remote add pess-upstream $UPDATE_BASE 2>$null | Out-Null
git remote set-url pess-upstream $UPDATE_BASE 2>$null | Out-Null
git fetch pess-upstream main --tags 2>&1 | Out-Null

# Checkout updated templates and scripts (but never overwrite user customizations)
# Protected: CLAUDE.md, memory-bank/
Write-Host "Updating templates and scripts..." -ForegroundColor Cyan
$protected = @("CLAUDE.md", "memory-bank", "LICENSE", "README.md")

# Stage files we want to update from upstream
$updatePaths = @("templates/", "hooks/", "pess-install.ps1", "pess-init.ps1", "pess-update.ps1", "AGENTS.md", "CHANGELOG.md", ".gitignore")

foreach ($path in $updatePaths) {
    git checkout pess-upstream/main -- $path 2>$null | Out-Null
}

Write-Host ""
Write-Host "PESS has been updated to the latest version." -ForegroundColor Green
Write-Host ""
Write-Host "Files that were NOT overwritten (your customizations preserved):" -ForegroundColor Yellow
foreach ($f in $protected) {
    Write-Host "  - $f"
}
Write-Host ""

$latestTag = (Get-LatestTag) -replace 'v', ''
if ($null -eq $latestTag) { $latestTag = $CURRENT_VERSION }
Write-Host "Current version: v$CURRENT_VERSION"
Write-Host "Latest version: v$latestTag"

if ($latestTag -ne $CURRENT_VERSION) {
    Write-Host "What's new:" -ForegroundColor Cyan
    Write-Host "  Visit https://github.com/qianbkk/pess/releases/v$latestTag" -ForegroundColor White
    Write-Host "  Or run: git fetch origin && git checkout v$latestTag" -ForegroundColor White
}