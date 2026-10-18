## MODIFIED Requirements

### Requirement: Active checkpoints SHALL remain load-compatible

清理与部署迁移 SHALL 保持当前 LIGER 与正式 CoPMRec v2 checkpoint 的输入身份检查和严格恢复；旧 CoPMRec 开发 checkpoint SHALL NOT 被改标签当作当前正式版本恢复。CoPMRec 的训练 checkpoint 身份 SHALL 与本次 hybrid/dense 部署契约分离，允许复用已有正式 own-best，不改写文件或放松目标、变体、seed、预算与完整状态校验。

#### Scenario: Load current CoPMRec checkpoint state

- **WHEN** checkpoint 来自相同正式版本、损失契约与输入目录
- **THEN** 当前模型严格恢复状态，并在相同部署模式下保持预测一致；显式部署切换由独立契约标注，旧版本或身份不匹配的 checkpoint 被拒绝
