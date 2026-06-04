"""PESS PostToolUse 自动 lint hook (OPT-004)

监听 PostToolUse:Write|Edit 事件,按文件后缀调用对应 linter:
- .py  → ruff (no flake8 fallback in v1)
- .js/.ts/.tsx/.jsx  → eslint (+ tsc for .ts)
- .md  → markdownlint (无 fallback, 静默跳过)

异步执行 (subprocess.Popen + timeout 5s),不阻塞 AI 写流程
linter 不存在时静默返回 (graceful degradation)
linter 崩溃/panic 时静默退出,只在 stderr 提示 (避免被误判为 lint 通过)
"""
import json
import os
import shutil
import subprocess
import sys

# Windows GBK stdout 修复
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LINTERS = {
    ".py":  [("ruff",   ["ruff", "check", "--output-format", "concise", "--no-fix"])],
    ".js":  [("eslint", ["eslint", "--no-fix", "--format", "compact"])],
    ".ts":  [("eslint", ["eslint", "--no-fix", "--format", "compact"]),
             ("tsc",    ["tsc", "--noEmit", "--pretty", "false"])],
    ".tsx": [("eslint", ["eslint", "--no-fix", "--format", "compact"])],
    ".jsx": [("eslint", ["eslint", "--no-fix", "--format", "compact"])],
    ".md":  [("markdownlint", ["markdownlint", "--json"])],
}

# 超时可由环境变量 PESS_LINT_TIMEOUT 覆盖,默认 5s
TIMEOUT_SECONDS = int(os.environ.get("PESS_LINT_TIMEOUT", "5"))

# linter 崩溃信号词: 含这些词的输出视为 linter 自身故障而非 lint issue
LINTER_CRASH_SIGNALS = ("error: ", "fatal:", "panic:", "internal error", "traceback")


def find_file(tool_input):
    """从 Write/Edit/MultiEdit 的 tool_input 提取文件路径 (Claude Code 官方只用 file_path)"""
    return tool_input.get("file_path", "")


def get_linter_for(path):
    ext = os.path.splitext(path)[1].lower()
    return LINTERS.get(ext)


def has_linter(linter_name):
    """检查 linter 是否在 PATH 中 (使用 shutil.which, 零子进程开销)"""
    return shutil.which(linter_name) is not None


def looks_like_crash(output, returncode):
    """区分 'linter 崩溃' vs 'linter 报告了真实 issue'

    规则:
    - returncode == 0 → 无问题
    - returncode in (1, 2) 且有 issue 行输出 → 真实 lint 问题
    - returncode >= 3 或输出含 crash 信号词 → linter 自身故障
    """
    if returncode == 0:
        return False
    if returncode >= 3:
        return True
    output_lower = output.lower()
    return any(sig in output_lower for sig in LINTER_CRASH_SIGNALS)


def run_linter(cmd, file_path):
    """异步执行 linter,返回 (warning_count, summary_message, is_crash)"""
    try:
        proc = subprocess.Popen(
            cmd + [file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout, stderr = proc.communicate(timeout=TIMEOUT_SECONDS)
        output = (stdout + stderr).strip()
        # 区分崩溃 vs 真实问题
        if looks_like_crash(output, proc.returncode):
            return 0, f"linter crashed (rc={proc.returncode}): {output[:300]}", True
        if proc.returncode == 0:
            return 0, "", False
        # 真实 lint 问题: 统计非空行作为 issue 数
        lines = [l for l in output.splitlines() if l.strip()]
        return len(lines), output[:500], False
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        return 0, f"linter timeout (>{TIMEOUT_SECONDS}s)", True
    except FileNotFoundError:
        return 0, f"linter not found: {cmd[0]}", True
    except Exception as e:
        return 0, f"linter error: {e}", True


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # fail-open: stdin 异常不阻断用户
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = find_file(tool_input)
    if not file_path:
        sys.exit(0)

    # 安全检查 (B3 修复): 防止 file_path 是 flag 注入或文件不存在
    if file_path.startswith("-"):
        sys.exit(0)
    if not os.path.isfile(file_path):
        sys.exit(0)

    candidates = get_linter_for(file_path)
    if not candidates:
        # 文件后缀无对应 linter, 静默通过
        sys.exit(0)

    # 找第一个可用的 linter
    for linter_name, cmd in candidates:
        if not has_linter(linter_name):
            continue
        warning_count, summary, is_crash = run_linter(cmd, file_path)
        if is_crash:
            # linter 自身故障 (B1 修复): 必须显式告知用户, 避免"静默成功"假象
            print(f"⚠️  lint skipped (linter error): {summary}", file=sys.stderr)
            sys.exit(0)
        if warning_count == 0:
            # 无问题, 静默通过
            sys.exit(0)
        # 有 lint 问题, 输出 warn JSON
        # PostToolUse 协议: 软警告用 exit 0 + stderr, Claude Code 会展示给用户
        print(json.dumps({
            "tool_name": tool_name,
            "file": file_path,
            "linter": linter_name,
            "warning_count": warning_count,
            "message": f"⚠️  {linter_name} 发现 {warning_count} 项问题:\n{summary}",
        }), file=sys.stderr)
        sys.exit(0)

    # 所有候选 linter 都不可用, 静默通过
    sys.exit(0)


if __name__ == "__main__":
    main()
