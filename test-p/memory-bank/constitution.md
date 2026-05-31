# test-p 椤圭洰瀹硶

> 杩欐槸椤圭洰鐨勬渶楂樿鑼冦€傛墍鏈夊悗缁紑鍙戝繀椤婚伒瀹堜互涓嬪師鍒欍€?
## 涓嶅彲鍗忓晢鍘熷垯

### 璐ㄩ噺搴曠嚎
- 娴嬭瘯瑕嗙洊鐜? service 灞?鈮?85%锛孉PI 灞?鈮?70%
- 绂佹瑁?except/catch锛屽繀椤绘寚瀹氬紓甯哥被鍨?
### 瀹夊叏绾㈢嚎
- 绂佹鍦ㄤ唬鐮佷腑纭紪鐮?secret/token/key
- 鎵€鏈夌敤鎴疯緭鍏ュ繀椤荤粡杩囨樉寮忛獙璇?
### 椤圭洰鐗瑰畾绾︽潫
锛堝緟濉啓锛?"@

# 澶嶅埗 Skills锛堥€氱敤 + simulation 绫诲瀷涓撶敤锛? = Join-Path D:\AI\Claude code workspace\A6.1\PESS "templates\skills"
 = Join-Path D:\AI\Claude code workspace\A6.1\PESS\test-p ".claude/skills"
if (Test-Path ) {
    Copy-Item "\security-patterns.md"  -ErrorAction SilentlyContinue
    Copy-Item "\testing-patterns.md"   -ErrorAction SilentlyContinue
    if (default -eq "simulation") {
        Copy-Item "\simulation.md"  -ErrorAction SilentlyContinue
    }
}

# 澶嶅埗 Commands
 = Join-Path D:\AI\Claude code workspace\A6.1\PESS "templates\commands"
 = Join-Path D:\AI\Claude code workspace\A6.1\PESS\test-p ".claude/commands"
if (Test-Path ) {
    Copy-Item "\*.md"  -ErrorAction SilentlyContinue
}

# 鍒濆鍖?git
Set-Location D:\AI\Claude code workspace\A6.1\PESS\test-p
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
