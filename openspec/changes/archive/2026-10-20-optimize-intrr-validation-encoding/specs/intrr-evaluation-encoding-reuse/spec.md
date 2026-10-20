## ADDED Requirements

### Requirement: 单 batch 复用历史编码

IntRR SHALL 在 eval 模式的 validation_step 和 test_step 中只编码一次历史，并保持原有评估张量逐元素一致。

#### Scenario: 验证与测试输出等价
- **WHEN** 同一权重、输入和标签分别经过旧 losses + generate 路径和评估路径
- **THEN** loss、sid_loss、alignment_loss、generated_ids、marginal_probs、labels SHALL 完全一致，评估 backbone 调用次数 SHALL 为一次。

### Requirement: 保持训练与 checkpoint 兼容

IntRR SHALL 保持训练损失、梯度、公共生成接口和 checkpoint 身份契约。

#### Scenario: 原模型继续加载和训练
- **WHEN** 加载原 state_dict 和 intrr_contract 并执行训练或预测
- **THEN** strict 加载 SHALL 成功，共享 RAN 各参数 SHALL 保持有限梯度，合法 beam 与预测输出契约 SHALL 保持。
