# pess-install.ps1 — 安装 PESS 全局组件（只需运行一次）

$PessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClaudeDir = "$env:USERPROFILE\.claude"
$HooksDir  = "$ClaudeDir\hooks"

# 1. 确保目录存在
New-Item -ItemType Directory -Force -Path $HooksDir | Out-Null

# 2. 复制 hooks
Copy-Item "$PessRoot\hooks\guard_files.py"    $HooksDir -Force
Copy-Item "$PessRoot\hooks\guard_commands.py" $HooksDir -Force
Copy-Item "$PessRoot\hooks\auto_lint.py"      $HooksDir -Force
Copy-Item "$PessRoot\hooks\inject_context.py" $HooksDir -Force
Write-Host "Hooks 已安装到 $HooksDir" -ForegroundColor Green

# 3. 验证 Python 可用性
$pythonOk = $false
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        # 修复(OPT-003): 在 "3\.1[0-9]" 前加 "Python " 前缀
        # 原写法 "Python 3\.[89]|3\.1[0-9]|Python 3\.1[2-9]" 中,
        # 单独的 "3\.1[0-9]" 没有 Python 前缀, 可能误判含 "3.10" 字面量的字符串
        if ($ver -match "^Python 3\.[89]|^Python 3\.1[0-9]|^Python 3\.1[2-9]") {
            Write-Host "Python 检测: $ver ✅" -ForegroundColor Green
            $pythonOk = $true
            break
        }
    } catch {}
}
if (-not $pythonOk) {
    Write-Warning "未检测到 Python 3.8+。hooks 已安装但可能无法运行，请确保 Python 3.8+ 在 PATH 中。"
}

# 4. 写入或合并 settings.json
$settingsPath = "$ClaudeDir\settings.json"

$newHooksWrite = @{ type = "command"; command = "python `"$HooksDir\guard_files.py`"" }
$newHooksBash  = @{ type = "command"; command = "python `"$HooksDir\guard_commands.py`"" }
$newHooksPost  = @{ type = "command"; command = "python `"$HooksDir\auto_lint.py`"" }
$newHooksStart = @{ type = "command"; command = "python `"$HooksDir\inject_context.py`"" }

if (Test-Path $settingsPath) {
    # 合并到现有 settings.json，不覆盖已有内容
    $existing = Get-Content $settingsPath -Raw | ConvertFrom-Json

    if (-not $existing.hooks) {
        $existing | Add-Member -NotePropertyName "hooks" -NotePropertyValue @{} -Force
    }
    if (-not $existing.hooks.PreToolUse) {
        $existing.hooks | Add-Member -NotePropertyName "PreToolUse" -NotePropertyValue @() -Force
    }
    if (-not $existing.hooks.PostToolUse) {
        $existing.hooks | Add-Member -NotePropertyName "PostToolUse" -NotePropertyValue @() -Force
    }
    if (-not $existing.hooks.SessionStart) {
        $existing.hooks | Add-Member -NotePropertyName "SessionStart" -NotePropertyValue @() -Force
    }

    # 检查 guard_files 是否已注册（避免重复）
    $alreadyHasFiles = $false
    if ($existing.hooks -and $existing.hooks.PreToolUse) {
        foreach ($entry in $existing.hooks.PreToolUse) {
            if ($entry.hooks -and ($entry.hooks | Where-Object { $_.command -like "*guard_files*" })) {
                $alreadyHasFiles = $true
                break
            }
        }
    }
    if (-not $alreadyHasFiles) {
        $entry = @{
            matcher = "Write|Edit|MultiEdit"
            hooks   = @($newHooksWrite)
        }
        if ($existing.hooks.PreToolUse -is [array]) {
            $existing.hooks.PreToolUse += @($entry)
        } else {
            $existing.hooks.PreToolUse = @($entry)
        }
    }

    # 检查 guard_commands 是否已注册（避免重复）
    $alreadyHasBash = $false
    if ($existing.hooks -and $existing.hooks.PreToolUse) {
        foreach ($entry in $existing.hooks.PreToolUse) {
            if ($entry.hooks -and ($entry.hooks | Where-Object { $_.command -like "*guard_commands*" })) {
                $alreadyHasBash = $true
                break
            }
        }
    }
    if (-not $alreadyHasBash) {
        $entry = @{
            matcher = "Bash"
            hooks   = @($newHooksBash)
        }
        if ($existing.hooks.PreToolUse -is [array]) {
            $existing.hooks.PreToolUse += @($entry)
        } else {
            $existing.hooks.PreToolUse = @($entry)
        }
    }

    # 检查 auto_lint 是否已注册到 PostToolUse (避免重复) — OPT-004
    $alreadyHasLint = $false
    if ($existing.hooks.PostToolUse) {
        foreach ($entry in $existing.hooks.PostToolUse) {
            if ($entry.hooks -and ($entry.hooks | Where-Object { $_.command -like "*auto_lint*" })) {
                $alreadyHasLint = $true
                break
            }
        }
    }
    if (-not $alreadyHasLint) {
        $entry = @{
            matcher = "Write|Edit|MultiEdit"
            hooks   = @($newHooksPost)
        }
        if ($existing.hooks.PostToolUse -is [array]) {
            $existing.hooks.PostToolUse += @($entry)
        } else {
            $existing.hooks.PostToolUse = @($entry)
        }
    }

    # 检查 inject_context 是否已注册到 SessionStart (避免重复) — OPT-005
    $alreadyHasInject = $false
    if ($existing.hooks.SessionStart) {
        foreach ($entry in $existing.hooks.SessionStart) {
            if ($entry.hooks -and ($entry.hooks | Where-Object { $_.command -like "*inject_context*" })) {
                $alreadyHasInject = $true
                break
            }
        }
    }
    if (-not $alreadyHasInject) {
        $entry = @{
            hooks = @($newHooksStart)
        }
        if ($existing.hooks.SessionStart -is [array]) {
            $existing.hooks.SessionStart += @($entry)
        } else {
            $existing.hooks.SessionStart = @($entry)
        }
    }

    $existing | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Host "Hooks 已合并到现有 settings.json" -ForegroundColor Green
} else {
    # 全新安装
    @{
        hooks = @{
            PreToolUse = @(
                @{ matcher = "Write|Edit|MultiEdit"; hooks = @($newHooksWrite) },
                @{ matcher = "Bash";                 hooks = @($newHooksBash) }
            )
            PostToolUse = @(
                @{ matcher = "Write|Edit|MultiEdit"; hooks = @($newHooksPost) }
            )
            SessionStart = @(
                @{ hooks = @($newHooksStart) }
            )
        }
    } | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Host "settings.json 已创建" -ForegroundColor Green
}

# 5. 复制全局 CLAUDE.md（如已存在则跳过，不覆盖用户的定制）
$globalTarget = "$ClaudeDir\CLAUDE.md"
if (-not (Test-Path $globalTarget)) {
    Copy-Item "$PessRoot\templates\global-CLAUDE.md" $globalTarget
    Write-Host "全局 CLAUDE.md 已安装，请打开并填写你的个人信息" -ForegroundColor Green
} else {
    Write-Host "全局 CLAUDE.md 已存在，跳过（不覆盖）" -ForegroundColor Yellow
}

Write-Host "`nPESS 安装完成。" -ForegroundColor Cyan
Write-Host "下一步：编辑 $globalTarget 填写你的个人规范" -ForegroundColor White