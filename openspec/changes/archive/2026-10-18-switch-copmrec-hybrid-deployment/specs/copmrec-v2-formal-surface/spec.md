## MODIFIED Requirements

### Requirement: 单一正式运行面

系统 SHALL 使用 CoPMRec v2 默认训练、dense 验证与 hybrid 推理；三目标为 SID CE、joint catalog CE、mixture NLL，所有阶段无历史排除；旧 native view 和迭代入口 SHALL 归档移出运行面。显式 dense 辅助推理 SHALL 保留以复现旧 dense 评分证据；hits 主部署分析 SHALL 使用同一 hybrid 协议的四份产物，原 residual 全目录分析 SHALL 保留 dense 身份。

#### Scenario: 默认入口

- **WHEN** 用户 compose copmrec_train 或 copmrec_inference
- **THEN** 获得 v2 模型与准确的无排除配置；训练双卡且 dense 选优，推理单卡 hybrid，严格恢复自身 checkpoint 并记录独立部署契约

#### Scenario: 机制输入协议一致

- **WHEN** hits 分析接收混合 dense 与 hybrid 部署身份的输入
- **THEN** 系统拒绝混用；同一 hybrid 协议的四份已核验预测可用于主部署 hits 分析，旧 residual 分析继续消费 dense reference
