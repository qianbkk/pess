"""PESS PostToolUse 自动 lint hook (OPT-004)

监听 PostToolUse:Write|Edit 事件,按文件后缀调用对应 linter:
- .py  → ruff (fallback: flake8)
- .js/.ts/.tsx/.jsx  → eslint
- .md  → markdownlint (fallback: 无, 静默跳过)

异步执行 (subprocess.Popen + timeout 5s),不阻塞 AI 写流程
linter 不存在时静默返回 (graceful degradation)
"""
import json
import os
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

TIMEOUT_SECONDS = 5


def find_file(tool_input):
    """从 Write/Edit/MultiEdit 的 tool_input 提取文件路径"""
    return tool_input.get("file_path") or tool_input.get("path", "")


def get_linter_for(path):
    ext = os.path.splitext(path)[1].lower()
    return LINTERS.get(ext)


def has_linter(linter_name):
    """检查 linter 是否在 PATH 中 (避免阻塞在 'command not found')"""
    try:
        result = subprocess.run(
            [linter_name, "--version"],
            capture_output=True,
            timeout=1,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def run_linter(cmd, file_path):
    """异步执行 linter,返回 (warning_count, summary_message)"""
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
        # linter 返回非 0 通常表示有问题
        if proc.returncode == 0:
            return 0, ""
        # 提取 issue 数量 (粗略统计: 多少行输出 / 多少 'error' 出现)
        output = (stdout + stderr).strip()
        lines = [l for l in output.splitlines() if l.strip()]
        return len(lines), output[:500]
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, "linter timeout (>5s)"
    except FileNotFoundError:
        return -2, f"linter not found: {cmd[0]}"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # fail-open: stdin 异常不阻断用户
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = find_file(tool_input)
    if not file_path:
        sys.exit(0)

    candidates = get_linter_for(file_path)
    if not candidates:
        # 文件后缀无对应 linter, 静默通过
        sys.exit(0)

    # 找第一个可用的 linter
    for linter_name, cmd in candidates:
        if not has_linter(linter_name):
            continue
        warning_count, summary = run_linter(cmd, file_path)
        if warning_count == 0:
            # 无问题, 静默通过
            sys.exit(0)
        if warning_count < 0:
            # linter 内部错误 (-1=timeout, -2=not found)
            # 不阻断用户, 仅 stderr 提示
            print(f"⚠️  lint skipped: {summary}", file=sys.stderr)
            sys.exit(0)
        # 有 lint 问题, 输出 warn JSON
        # PostToolUse 协议: 软警告用 exit 0 + stderr, Claude Code 会展示给用户
        print(json.dumps({
            "action": "warn",
            "tool_name": tool_name,
            "file": file_path,
            "linter": linter_name,
            "warning_count": warning_count,
            "message": f"⚠️  {linter_name} 发现 {warning_count} 项问题:\n{summary}",
        }), file=sys.stderr)
        sys.exit(0)

    # 所有候选 linter 都不可用
    sys.exit(0)


if __name__ == "__main__":
    main()
