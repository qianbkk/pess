# pess-install.ps1 — PESS 安装 shim (v3.8.0)
#
# 权威源已迁移到 pess.py (Python), 本脚本为向后兼容薄包装.
# 详细安装逻辑见 pess.py cmd_install.

$ErrorActionPreference = "Stop"
$PessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 调用 Python 统一入口
try {
    python "$PessRoot\pess.py" install
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "pess.py install returned $LASTEXITCODE"
    }
} catch {
    Write-Error "Failed to run python pess.py install: $_"
    Write-Error "Python 3.8+ required and pess.py must be in PATH"
    exit 1
}

Write-Host ""
Write-Host "✅ PESS 安装完成 (via pess.py 权威源)" -ForegroundColor Green
Write-Host "如需自定义: python pess.py install --help" -ForegroundColor Cyan
