---
name: freeze
description: "Use when user wants to lock a directory from writes. Triggers .pess-freeze.json update. Do not load for read-only access."
---

# /freeze — 目录级写锁定 (OPT-015)

> **触发条件**: 用户输入 /freeze <path> 锁定目录
> **行为**: 列出目录中的所有 Read/Write/Edit 操作都被 block

---

## 工作流程

### 1. 锁定命令

```
/freeze src/migrations/
# 输出:
# 🔒 src/migrations/ 已冻结
# - Read 仍允许
# - Write/Edit/MultiEdit 已 block
# - 解除: /unfreeze src/migrations/
```

### 2. 维护 .pess-freeze 列表

```
# ~/.claude/pess-freeze.json
{
  "frozen_paths": [
    "src/migrations/",
    ".env",
    "production.config"
  ]
}
```

### 3. 守护逻辑（在 `guard_files.py` 中读取 .pess-freeze.json）

```python
def is_frozen(file_path: str) -> bool:
    # 始终允许的目录
    WHITELIST = {".git/", ".claude/"}
    for white in WHITELIST:
        if file_path.startswith(white):
            return False
    # 检查冻结列表
    for frozen in load_freeze_list():
        if file_path.startswith(frozen) or file_path == frozen:
            return True
    return False
```

### 4. 默认白名单 (永远不冻结)

- `.git/`
- `.claude/`
- `README.md`
- `LICENSE`
- `CHANGELOG.md`

---

## 紧急解锁

```
/unfreeze <path>     # 解锁指定目录
/unfreeze --all      # 解锁全部
```

---

## 误锁防护

- 锁定操作需要二次确认: "确认冻结 src/migrations/? [y/N]"
- 锁定前显示该目录将影响哪些文件
- 保留至少一个未冻结的"逃生通道"目录
