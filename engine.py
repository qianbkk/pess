"""PESS 模板引擎 3 原语 (OPT-013)

3 原语: 变量替换 / 条件块 / 循环
拒绝: from_prev_command (辩论报告 §arch#4 修改)

不引入 jinja2 依赖, 用 AST 简单解析
"""
import re
from typing import Any, Dict

VAR_PATTERN = re.compile(r"\{\{\s*([\w.]+)(?:\s*\|\s*default:\s*['\"]([^'\"]*)['\"])?\s*\}\}")
IF_PATTERN = re.compile(r"\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}", re.DOTALL)
FOR_PATTERN = re.compile(r"\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}(.*?)\{%\s*endfor\s*%\}", re.DOTALL)


def resolve_value(context: Dict[str, Any], dotted: str, default: str = None) -> str:
    """从 context 解析嵌套 key, 支持默认值"""
    parts = dotted.split(".")
    value = context
    try:
        for p in parts:
            value = value[p]
        return str(value)
    except (KeyError, TypeError):
        return default if default is not None else ""


def render(template: str, context: Dict[str, Any]) -> str:
    """渲染模板: 3 原语组合

    1. 变量: {{ var }} 或 {{ var|default:"x" }}
    2. 条件: {% if cond %}...{% endif %}
    3. 循环: {% for item in list %}...{% endfor %}

    实现: 自顶向下递归处理, 每次 render 调用逐层剥离最外层语法
    """
    # 找到最外层 {% %} 块的位置, 块内文本直接递归 render
    # 这样能正确处理 for→if→var 的嵌套
    result = []
    i = 0
    while i < len(template):
        # 找下一个 {% 块标记 (不跨行, 避免吞换行)
        m = re.search(r"\{%[^{}%]*%\}", template[i:])
        if not m:
            # 剩余是普通文本, 替换变量
            result.append(_render_vars(template[i:], context))
            break
        # 块标记前是普通文本
        result.append(_render_vars(template[i:i + m.start()], context))
        tag = m.group(0)
        # 解析 tag 类型
        if tag.startswith("{% if "):
            mif = re.match(r"\{%\s*if\s+(\w+)\s*%\}", tag)
            if not mif:
                i += m.end()
                continue
            cond = mif.group(1)
            end_tag = "{% endif %}"
            block_end = _find_block_end(template, i + m.end(), "if", end_tag)
            if block_end is None:
                raise ValueError("unmatched {% if %}")
            inner = template[i + m.end():block_end]
            # 支持 {% else %} 分支
            else_pos = inner.find("{% else %}")
            if else_pos != -1:
                true_part = inner[:else_pos]
                false_part = inner[else_pos + len("{% else %}"):]
            else:
                true_part = inner
                false_part = ""
            if context.get(cond):
                result.append(render(true_part, context))
            else:
                result.append(render(false_part, context))
            i = block_end + len(end_tag)
        elif tag.startswith("{% for "):
            mfor = re.match(r"\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}", tag)
            var_name, list_path = mfor.group(1), mfor.group(2)
            end_tag = "{% endfor %}"
            block_end = _find_block_end(template, i + m.end(), "for", end_tag)
            if block_end is None:
                raise ValueError("unmatched {% for %}")
            inner = template[i + m.end():block_end]
            items = context.get(list_path, [])
            if isinstance(items, list):
                for item in items:
                    result.append(render(inner, {**context, var_name: item}))
            i = block_end + len(end_tag)
        else:
            # 未知 tag, 跳过
            i += m.end()
    return "".join(result)


def _find_block_end(template: str, start: int, block_type: str, end_tag: str) -> int:
    """找到 {% endif %} 或 {% endfor %} 块的结束位置, 处理嵌套

    块可以是 if 或 for, end_tag 分别是 {% endif %} 或 {% endfor %}.
    """
    depth = 1
    # 用更宽泛的 open_tag 匹配: {% if 或 {% for
    if block_type == "if":
        open_pattern = re.compile(r"\{%\s*if\s+")
    else:
        open_pattern = re.compile(r"\{%\s*for\s+")
    i = start
    while i < len(template):
        # 找下一个 open
        m_open = open_pattern.search(template, i)
        next_open = m_open.start() if m_open else -1
        # 找下一个 close
        next_close = template.find(end_tag, i)
        if next_close == -1:
            return None
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 5  # 跳过 "{% if" 或 "{% for"
        else:
            depth -= 1
            if depth == 0:
                return next_close
            i = next_close + len(end_tag)
    return None


def _render_vars(text: str, context: Dict[str, Any]) -> str:
    """仅替换 {{ var }} 变量"""
    def replace_var(m):
        key = m.group(1)
        default = m.group(2)
        return resolve_value(context, key, default)
    return VAR_PATTERN.sub(replace_var, text)


if __name__ == "__main__":
    # 简单自测
    ctx = {"name": "PESS", "use_db": True, "endpoints": ["/users", "/posts"]}
    tpl = """# {{ name }}
{% if use_db %}Database enabled{% endif %}
{% for ep in endpoints %}- {{ ep }}
{% endfor %}"""
    print(render(tpl, ctx))
