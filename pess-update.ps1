# pess-update.ps1 — Update PESS to latest version (Windows)
# Usage: .\pess-update.ps1 [-CheckOnly]

param(
    [switch]$CheckOnly
)

$CURRENT_VERSION = "3.1.0"
$UPDATE_BASE = "https://github.com/qianbkk/pess.git"

Write-Host "PESS Updater v$CURRENT_VERSION" -ForegroundColor Cyan

if ($CheckOnly) {
    Write-Host "Checking for updates..."
    # Compare with local tag
    try {
        $latestTag = git describe --tags 2>$null | ForEach-Object { $_ -replace 'v', '' }
        if ($null -eq $latestTag) { $latestTag = $CURRENT_VERSION }
    } catch {
        $latestTag = $CURRENT_VERSION
    }
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

# Pull latest changes
git remote add pess-upstream $UPDATE_BASE 2>$null | Out-Null
git remote set-url pess-upstream $UPDATE_BASE 2>$null | Out-Null

Write-Host "Pulling PESS updates..." -ForegroundColor Cyan
git fetch pess-upstream main --tags 2>&1 | Out-Null

Write-Host ""
Write-Host "PESS has been updated to the latest version." -ForegroundColor Green
Write-Host ""
Write-Host "Files that were NOT overwritten (your customizations preserved):" -ForegroundColor Yellow
Write-Host "  - CLAUDE.md"
Write-Host "  - memory-bank/"
Write-Host ""

$latestTag = git describe --tags --abbrev=0 2>$null -replace 'v', ''
if ($null -eq $latestTag) { $latestTag = $CURRENT_VERSION }
Write-Host "Current version: v$CURRENT_VERSION"
Write-Host "Latest version: v$latestTag"