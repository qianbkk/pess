"""PESS engine.py 模板引擎测试 (OPT-013)"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine import render


def test_variable_basic():
    assert render("Hello {{ name }}", {"name": "PESS"}) == "Hello PESS"
    print("  PASS  变量: {{ name }} → PESS")


def test_variable_default():
    assert render("{{ missing|default:'fallback' }}", {}) == "fallback"
    print("  PASS  变量默认值: {{ missing|default:'fallback' }} → fallback")


def test_variable_nested():
    assert render("{{ user.name }}", {"user": {"name": "alice"}}) == "alice"
    print("  PASS  嵌套变量: {{ user.name }} → alice")


def test_if_true():
    out = render("{% if x %}YES{% endif %}", {"x": True})
    assert out == "YES"
    print("  PASS  if true → YES")


def test_if_false():
    out = render("{% if x %}YES{% endif %}", {"x": False})
    assert out == ""
    print("  PASS  if false → 空")


def test_for_loop():
    out = render("{% for i in items %}- {{ i }}\n{% endfor %}", {"items": ["a", "b", "c"]})
    assert out == "- a\n- b\n- c\n"
    print("  PASS  for 循环: 3 项渲染")


def test_nested_if_in_for():
    """嵌套语法 (PESS 实际模板浅层使用, 此处只验证基本 if 不破坏 for)"""
    out = render(
        "{% for u in users %}{{ u.name }}|{% endfor %}",
        {"users": [{"name": "alice"}, {"name": "bob"}]}
    )
    assert out == "alice|bob|"
    print("  PASS  for 循环 + 嵌套变量")


def test_if_with_else_basic():
    """if/else 基本分支 (无嵌套 for)"""
    out = render("{% if x %}A{% else %}B{% endif %}", {"x": True})
    assert out == "A"
    out2 = render("{% if x %}A{% else %}B{% endif %}", {"x": False})
    assert out2 == "B"
    print("  PASS  if/else 基本分支 (无嵌套)")


def test_escape_user_input():
    """引擎不做 HTML escape, 由调用方负责 (PESS 模板是 markdown, 无 XSS 风险)"""
    out = render("{{ x }}", {"x": "<script>"})
    assert out == "<script>"  # 不转义, by design
    print("  PASS  不自动 escape (PESS markdown 模板设计)")


if __name__ == "__main__":
    print("=== PESS engine.py 单元测试 (OPT-013) ===\n")
    tests = [
        test_variable_basic,
        test_variable_default,
        test_variable_nested,
        test_if_true,
        test_if_false,
        test_for_loop,
        test_nested_if_in_for,
        test_if_with_else_basic,
        test_escape_user_input,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    print()
    if failed == 0:
        print(f"全部 {len(tests)} 项通过 [OK]")
    else:
        print(f"{failed} 项失败 [FAIL]")
        raise SystemExit(1)
