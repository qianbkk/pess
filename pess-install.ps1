# pess-install.ps1 — 安装 PESS 全局组件（只需运行一次）

$PessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClaudeDir = "$env:USERPROFILE\.claude"
$HooksDir  = "$ClaudeDir\hooks"

# 1. 确保目录存在
New-Item -ItemType Directory -Force -Path $HooksDir | Out-Null

# 2. 复制 hooks
Copy-Item "$PessRoot\hooks\guard_files.py"    $HooksDir -Force
Copy-Item "$PessRoot\hooks\guard_commands.py" $HooksDir -Force
Write-Host "Hooks 已安装到 $HooksDir" -ForegroundColor Green

# 3. 写入 settings.json（如已存在则合并，不覆盖）
$settingsPath = "$ClaudeDir\settings.json"
$newHooks = @{
    hooks = @{
        PreToolUse = @(
            @{
                matcher = "Write|Edit|MultiEdit"
                hooks   = @(
                    @{ type = "command"; command = "python `"$HooksDir\guard_files.py`"" }
                )
            },
            @{
                matcher = "Bash"
                hooks   = @(
                    @{ type = "command"; command = "python `"$HooksDir\guard_commands.py`"" }
                )
            }
        )
    }
}

if (Test-Path $settingsPath) {
    Write-Warning "$settingsPath 已存在，请手动合并 hooks 配置："
    $newHooks | ConvertTo-Json -Depth 10 | Write-Host
} else {
    $newHooks | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Host "settings.json 已写入" -ForegroundColor Green
}

# 4. 复制全局 CLAUDE.md（如已存在则跳过，不覆盖用户的定制）
$globalTarget = "$ClaudeDir\CLAUDE.md"
if (-not (Test-Path $globalTarget)) {
    Copy-Item "$PessRoot\templates\global-CLAUDE.md" $globalTarget
    Write-Host "全局 CLAUDE.md 已安装，请打开并填写你的个人信息" -ForegroundColor Green
} else {
    Write-Host "全局 CLAUDE.md 已存在，跳过（不覆盖）" -ForegroundColor Yellow
}

Write-Host "`nPESS 安装完成。" -ForegroundColor Cyan
Write-Host "下一步：编辑 $globalTarget 填写你的个人规范" -ForegroundColor White