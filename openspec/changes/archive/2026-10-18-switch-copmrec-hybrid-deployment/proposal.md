## Why

CoPMRec 主结果需要与 LIGER 使用一致的部署流程：有限 beam 候选、全部 cold 商品补入及候选内 dense 重排。当前正式入口锁定全目录 dense，临时进程干预缺少独立部署身份，不能承载正式主矩阵。

## What Changes

- 将 CoPMRec 默认推理切换为 hybrid20，保留 dense Validation、原 own-best 选点与显式 dense 辅助推理。
- 保留旧训练 checkpoint 的所有来源、目标、变体、seed、状态及 SHA 身份，新增独立部署契约，不伪改旧训练记录。
- Full、三臂消融和 fixed-alpha-one 使用相同候选池与重排规则，记录各自候选 alpha 策略。
- 将 hits 分析绑定新 hybrid 产物，保留原 residual dense 评分分析的独立身份。
- 用户授权的执行范围为 13 次正式推理（9 Full、3 消融、1 fixed alpha）及 1 次 hits 分析，新增训练预算为零；临时结果不冒充正式矩阵。

## Capabilities

### New Capabilities

- `copmrec-hybrid-deployment`: 定义与旧训练身份分离的 hybrid 主部署、显式 dense 辅助模式和预测元信息。

### Modified Capabilities

- `copmrec-joint-only-formal`: 最终主部署改为 hybrid；训练、dense Validation 和 checkpoint 来源不变。
- `copmrec-v2-formal-surface`: 主矩阵和 hits 分析使用可核验的 hybrid 产物，不重置原预算与证据。
- `active-research-method-surface`: 保留严格旧训练 checkpoint 恢复，区分相同部署下预测一致与显式部署切换。

## Impact

涉及 CoPMRec 构造器、retrieve、运行部署元信息、Hydra 配置、启动脚本验证、hits 标签检查及对应 CPU 单测。复用 LIGER 已有候选生成和重排，不增加依赖，不修改训练目标或原 checkpoint，不宣称计算或检索效率改善。
