# PESS 仓库规范

## 这是什么
PESS（Personal Engineering Standards System）是一个 AI 辅助编程的工程规范工具，
核心产物是模板文件和 PowerShell 初始化脚本。

## 修改规则
- templates/ 下的文件是只读模板，修改时必须考虑所有使用了该模板的项目
- hooks/ 下的脚本需要保持与 pess-install.ps1 中的路径一致
- 任何新增的 Skill 必须有符合触发器格式的 description 字段

## 禁令
- 禁止用 LLM 自动生成任何模板内容
- 禁止在 templates/ 里写死绝对路径
- 禁止修改 hooks/ 的文件名（pess-install.ps1 依赖这些名字）