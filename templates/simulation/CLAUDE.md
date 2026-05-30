# [PROJECT_NAME] 专属规范

## 技术栈（锁定版本）
- 仿真引擎: LS-DYNA
- 单位系统: cm-g-μs-Mbar（CGS 微秒制）
- 物理场: 冲击动力学、穿甲、侵彻

## 目录约定（违反视为错误）
- 输入文件: input/              → .k 文件，LS-DYNA 关键字
- 材料的材料模型: materials/    → Johnson-Cook、RHT 等参数
- 输出结果: output/             → d3plot, state 文件
- 脚本: scripts/               → Python 后处理脚本

## 仿真专属规范（最高优先级）
- 所有物理量必须标注单位，格式: [值] [单位]
- 速度换算: 500 m/s = 0.05 cm/μs
- 压强换算: 1 GPa = 0.01 Mbar
- 网格坐标精度: 小数点后4位

## 数值验证要求
- 侵彻深度结果必须与 Forrestal 半经验公式对比
- 速度偏差 > 5% 时输出警告并停止

## 架构决策（禁止推翻，需修改先问我）
- 材料模型: Johnson-Cook（钢）、RHT（混凝土）
- 状态方程: Gruneisen

## 项目专属禁令
- 禁止修改 materials/ 下的材料参数文件
- 禁止删除 output/ 下的任何结果文件