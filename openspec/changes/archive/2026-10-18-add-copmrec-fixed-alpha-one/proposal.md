## Why

当前 CoPMRec v2 的可学习 alpha 接近 1，但移除 mixture NLL 的已有消融无法区分混合训练与额外目录 CE 权重的作用。用户要求补充固定 alpha=1 与当前可学习混合的比较，需要精确端点训练、独立来源和匹配协议。

## What Changes

- 在现有消融训练及推理入口增加 `fixed_alpha_one`，保留三项目标与共享残差，仅将训练 mixture 固定为纯目录前缀 mass。
- 使用精确端点，冻结 gate，独立标记 checkpoint 契约，保留默认 Full 和原三臂身份。
- 补充 Beauty seed42 匹配实验计划、结构化配置、手动运行命令及 Linear 待执行任务；新增计划成本 50k，保留已完成成本。
- 验证端点损失与目录 CE / SID 深度的等价性、梯度、恢复隔离、Hydra compose 和脚本参数。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `copmrec-v2-formal-surface`：扩展训练消融允许的固定端点臂，并保持原机制分析和完成证据边界。

## Impact

涉及 CoPMRec 的 mixture / catalog / ablation、现有消融配置与根脚本、CPU 单元测试和研究计划；不新增依赖。默认正式模型、已完成 M2/M3 运行和产物保持原身份。完整训练与 Testing 由用户手动启动。
