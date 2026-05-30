#!/bin/bash
# pess-init.sh — Initialize a new PESS project (macOS/Linux)

set -e

PROJECT_NAME=""
PROJECT_TYPE="default"
DESCRIPTION=""

usage() {
    echo "Usage: $0 -n <project_name> [-t <project_type>] [-d <description>]"
    echo "  -n: Project name (required)"
    echo "  -t: Project type: default, python-fastapi, node-express, fullstack, simulation (default: default)"
    echo "  -d: Project description"
    exit 1
}

while getopts "n:t:d:h" opt; do
    case $opt in
        n) PROJECT_NAME="$OPTARG" ;;
        t) PROJECT_TYPE="$OPTARG" ;;
        d) DESCRIPTION="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: -n <project_name> is required"
    usage
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$PWD/$PROJECT_NAME"

echo "Initializing PESS project: $PROJECT_NAME (type: $PROJECT_TYPE)"

# Create directory structure
mkdir -p "$PROJECT_ROOT/.claude/commands"
mkdir -p "$PROJECT_ROOT/.claude/skills"
mkdir -p "$PROJECT_ROOT/memory-bank"
mkdir -p "$PROJECT_ROOT/docs/spec"
mkdir -p "$PROJECT_ROOT/docs/adr"
mkdir -p "$PROJECT_ROOT/src"
mkdir -p "$PROJECT_ROOT/tests"

# Generate CLAUDE.md from template
TEMPLATE_PATH="$SCRIPT_DIR/templates/$PROJECT_TYPE/CLAUDE.md"
TARGET_PATH="$PROJECT_ROOT/CLAUDE.md"

if [ -f "$TEMPLATE_PATH" ]; then
    cp "$TEMPLATE_PATH" "$TARGET_PATH"
    # Replace [PROJECT_NAME] placeholder
    sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" "$TARGET_PATH"
    echo "CLAUDE.md generated from template"
else
    echo "# $PROJECT_NAME" > "$TARGET_PATH"
    echo "Warning: template not found, using minimal CLAUDE.md"
fi

# Generate AGENTS.md
cat > "$PROJECT_ROOT/AGENTS.md" << 'EOF'
# AGENTS.md

## Build
- Install: TODO
- Run: TODO
- Test: TODO
- Lint: TODO

## Constraints
- Branch: never push directly to main
- Secrets: never hardcode; always use environment variables

## Architecture
- Pattern: TODO
EOF

# Initialize Memory Bank — 6 files
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

cat > "$PROJECT_ROOT/memory-bank/activeContext.md" << EOF
# 当前活跃上下文

更新时间: $TIMESTAMP

## 当前任务
正在实现: 项目初始化

## 刚完成
- [x] 项目结构创建

## 下一步
- [ ] 填写 CLAUDE.md 的技术栈和目录约定
- [ ] 填写 AGENTS.md 的 Build 命令
- [ ] 写第一个功能的 FEATURE_SPEC.md
EOF

cat > "$PROJECT_ROOT/memory-bank/systemPatterns.md" << EOF
# 系统架构模式
（待填写）
EOF

cat > "$PROJECT_ROOT/memory-bank/lessons.md" << EOF
# 踩坑记录
（首次使用时此文件为空，遇到值得记录的问题后通过 /wrap 添加）
EOF

cat > "$PROJECT_ROOT/memory-bank/session-notes.md" << EOF
# 会话笔记（自动写入，无需手动维护）
EOF

cat > "$PROJECT_ROOT/memory-bank/progress.md" << EOF
# 项目进度

更新时间: $TIMESTAMP

## 已完成
（每完成一个里程碑后记录）

## 已知问题
（待解决的技术债或 bug）

## 下一里程碑
（下一个目标）
EOF

cat > "$PROJECT_ROOT/memory-bank/constitution.md" << EOF
# [PROJECT_NAME] 项目宪法

> 这是项目的最高规范。所有后续开发必须遵守以下原则。

## 不可协商原则

### 质量底线
- 测试覆盖率: service 层 ≥ 85%，API 层 ≥ 70%
- 禁止裸 except/catch，必须指定异常类型

### 安全红线
- 禁止在代码中硬编码 secret/token/key
- 所有用户输入必须经过显式验证

### 项目特定约束
（待填写）
EOF

# Copy skills
SKILLS_SRC="$SCRIPT_DIR/templates/skills"
SKILLS_DEST="$PROJECT_ROOT/.claude/skills"
[ -d "$SKILLS_SRC" ] && cp "$SKILLS_SRC"/*.md "$SKILLS_DEST/" 2>/dev/null || true
# simulation type adds simulation skill
if [ "$PROJECT_TYPE" = "simulation" ]; then
    [ -f "$SKILLS_SRC/simulation.md" ] && cp "$SKILLS_SRC/simulation.md" "$SKILLS_DEST/"
fi

# Copy commands
CMDS_SRC="$SCRIPT_DIR/templates/commands"
CMDS_DEST="$PROJECT_ROOT/.claude/commands"
[ -d "$CMDS_SRC" ] && cp "$CMDS_SRC"/*.md "$CMDS_DEST/" 2>/dev/null || true

# Init git
cd "$PROJECT_ROOT"
git init
cat > "$PROJECT_ROOT/.gitignore" << 'EOF'
.env
.env.*
*.pem
*.key
__pycache__/
*.pyc
node_modules/
dist/
.DS_Store
EOF
git add -A
git commit -m "chore: init project with PESS v3.1"

echo ""
echo "Project '$PROJECT_NAME' initialized successfully."
echo "Next steps:"
echo "  1. Fill in CLAUDE.md (tech stack and conventions)"
echo "  2. Fill in AGENTS.md Build commands"
echo "  3. Use /think to start your first feature"