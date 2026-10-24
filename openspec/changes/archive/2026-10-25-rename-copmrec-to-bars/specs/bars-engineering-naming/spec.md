## ADDED Requirements

### Requirement: Active engineering entrypoints SHALL use BARS

当前模块、Python 标识符、Hydra 组件和 experiment、根脚本、测试 helper 及新 task/method 名称 SHALL 使用 bars/BARS。系统 SHALL 不提供 copmrec 工程入口 alias。

#### Scenario: Load canonical model
- **WHEN** 导入 src.recommendation.bars 或组合 bars_ablation_train
- **THEN** 使用 BARS／BARSAblation，原 variant 和配置行为不变

#### Scenario: Reject old engineering entrypoint
- **WHEN** 请求 copmrec_train 或旧包源码
- **THEN** 旧 experiment 不可组合且旧包源码不存在

### Requirement: Serialized identities SHALL remain compatible

已冻结 checkpoint 的 copmrec_* 字段、copmrec-* 协议 ID 与历史来源 SHALL 保持原值；重命名 SHALL 不放宽 seed、变体、选点、损失或完整训练状态校验。

#### Scenario: Restore pre-migration checkpoint
- **WHEN** BARS 恢复迁移前相同变体的小型完整 checkpoint
- **THEN** strict load 成功，参数、协议、loss 与 dense/hybrid 输出逐位一致

#### Scenario: Keep provenance
- **WHEN** 更新当前命令说明
- **THEN** 历史结果、归档和证据文件保持字节不变，旧 URI/SHA 不被改名
