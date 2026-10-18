## MODIFIED Requirements

### Requirement: 全阶段不排除历史商品

系统 SHALL 在训练目录支持集、raw dense Validation 及最终单卡 hybrid 推理中保留历史商品，继续使用完整历史输入和残差。hybrid SHALL 在生成与全部 cold 的候选并集内使用稳定 catalog-row 排名；显式 dense 辅助推理 SHALL 保留原全目录稳定排名。Validation 及 own-best 选点 SHALL 继续使用 dense。

#### Scenario: 历史商品位于候选中且分数最高

- **WHEN** 合法历史商品进入 hybrid 候选且原始 joint 分数位于候选 TopK
- **THEN** hybrid 推理保留该商品，排序不读取目标标签；dense Validation 与显式 dense 辅助继续保留完整目录内的历史商品

### Requirement: 独立可核验来源

系统 SHALL 保存严格的新正式版本契约和完整模型/optimizer/scheduler状态，拒绝将原Full或A3checkpoint改标签当作新的正式训练；SHALL 保留其已有实证供明确标注的选型分析。既有正式 v2 own-best SHALL 按其原训练契约严格恢复用于 hybrid 或显式 dense，部署差异 SHALL 由独立运行契约记录，不能改写旧 checkpoint 身份。

#### Scenario: 恢复来源不同

- **WHEN** 新入口收到旧Full、A3或不同版本/损失契约的checkpoint
- **THEN** 拒绝普通正式恢复；正式 v2 自身完整 checkpoint 可恢复，在相同部署模式下预测一致

#### Scenario: 切换已有正式权重的部署

- **WHEN** 用户将自身已验证 v2 own-best 交给 hybrid 预测
- **THEN** 模型状态严格恢复，原训练来源与文件SHA不变，发布独立 hybrid 部署身份
