## Why

用户已选择固定 alpha=0.5、移除 mixture NLL 的 Untied 版本作为 BARS 主方法。当前 W&B 和 M2 仍将旧 learned-alpha 三损失矩阵标为主结果，需要切换角色并准确恢复新矩阵待执行状态。

## What Changes

- 将旧 bars_main 的记录转入 history，已验收的新 Beauty/seed42 训练与两种测试转入 bars_main。
- 固化新主方法的显示默认值及当前研究状态，保留实际执行配置、模型/Artifact 身份和历史结果。
- 将 M2 父项及其余八个主矩阵单元改为 Todo，更新新版本命令；Shared 对照继续 Done。
- 记录新主矩阵 1/9 已完成，其余单元未启动；本次不运行训练或改论文数值。

## Capabilities

### New Capabilities

- `bars-main-design-selection`: 当前主版本选择、历史角色隔离及矩阵覆盖状态。

### Modified Capabilities

无。

## Impact

W&B display name/group、Linear 主矩阵说明与当前计划、研究状态、显示配置和定向配置验证。无模型或优化算法修改，无新增依赖。
