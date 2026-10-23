# bars-hybrid-validation-selection Specification

## Purpose
定义当前 BARS 主方法的 hybrid Validation、checkpoint 选择与跨协议恢复约束。九格重启及0/9是启动时点事实，完成状态由正式验收更新，不授权再次训练。

## Requirements
### Requirement: 主版本使用hybrid验证选点

系统MUST为当前固定alpha=0.5且无mixture loss的BARS主变体采用hybrid Validation，复用推荐的混合概率beam20、全部cold并集、目录logits稳定Top10且无历史排除；每500步监控val/ndcg@10首次最大值。

#### Scenario: 实际验证走候选流程

- **WHEN** 主版本执行validation_step
- **THEN** SHALL调用hybrid候选流程，高分但未生成的seen商品不得从全目录补入，cold与历史商品保持可选。

### Requirement: checkpoint保留选点来源

系统MUST记录真实训练选择模式与hybrid候选配置，保持旧dense契约兼容，并拒绝把不同选择模式或候选设置的checkpoint作为同一训练来源恢复。

#### Scenario: 跨协议恢复被拒绝

- **WHEN** dense来源checkpoint用于hybrid选点模型或反向恢复
- **THEN** SHALL明确拒绝且不修改原checkpoint。

### Requirement: 九格授权重启和预算独立登记

系统MUST停止此前dense八格队列，保留其日志、产物和已发生预算；核验Beauty42的dense来源后，新主矩阵九格均从scratch执行50k，共450k授权训练，禁止自动Testing或复用dense own-best。

#### Scenario: Beauty42纳入重训

- **WHEN** W&B真实配置确认qtyamris使用dense Validation
- **THEN** SHALL将Beauty42纳入新九格，使用新run ID、输出、端口和tmux，并将新hybrid选择协议已验收覆盖登记为0/9直至正式验收。
