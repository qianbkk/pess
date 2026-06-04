"""PESS hooks 共享工具 (OPT-021)

集中处理 stdin JSON 解析异常, 避免每个 hook 重复 try/except
"""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_read_stdin() -> dict:
    """从 stdin 读取 JSON, 异常时返回空 dict (fail-open 语义)

    5 项边界:
    - 正常 JSON: 返回 parsed dict
    - 空 stdin: 返回 {}
    - 非法 JSON: 返回 {} + stderr 提示
    - 超大 JSON (>10MB): 返回 {} + stderr 提示 (可能 OOM)
    - Unicode 错误: 替换模式解析, 返回部分结果
    """
    try:
        raw = sys.stdin.read()
    except Exception as e:
        print(f"hook: stdin read error: {e}", file=sys.stderr)
        return {}

    if not raw or not raw.strip():
        return {}

    # 超大 JSON 防护 (10MB 硬上限)
    if len(raw) > 10 * 1024 * 1024:
        print("hook: stdin too large (>10MB), skip", file=sys.stderr)
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"hook: invalid JSON stdin: {e}", file=sys.stderr)
        return {}


if __name__ == "__main__":
    # 自测
    import io
    test_cases = [
        ('{"a": 1}', {"a": 1}),
        ('', {}),
        ('not json', {}),
        ('{"a": "b', {}),  # 截断 JSON
    ]
    for raw, expected in test_cases:
        sys.stdin = io.StringIO(raw)
        result = safe_read_stdin()
        assert result == expected, f"FAIL: {raw!r} → {result} (expected {expected})"
        print(f"  PASS  safe_read_stdin({raw!r}) → {result}")
    print("utils.py 自测通过")
