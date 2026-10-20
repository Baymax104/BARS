# intrr-validation-rollout Specification

## Purpose
记录验证优化实现版本，并在前驱训练正常完成及来源核验通过后交接既有训练队列。保留新旧源码身份与原训练预算，同步未完成时保持后继等待。
## Requirements
### Requirement: 后继版本可追溯

IntRR 训练配置 SHALL 记录 `validation_implementation=history-encoding-reuse-v1`，所有 TIGER 外部协议参数 SHALL 保持。

#### Scenario: 新训练组合配置
- **WHEN** 组合 IntRR train experiment
- **THEN** 解析配置 SHALL 包含实现版本，trainer、data、optimizer、callbacks SHALL 继续匹配原 TIGER 协议测试。

### Requirement: 成功前驱之后切换

队列 SHALL 在当前训练自然退出 0 且新源码通过同步来源核验后才能放行后继。

#### Scenario: 当前训练未结束
- **WHEN** 交接状态为 preparing
- **THEN** 后继 guard SHALL 返回等待，当前训练 SHALL 持续使用原实现。

#### Scenario: 新版本已交接
- **WHEN** 前驱退出 0、Mutagen 三 session 正常且来源 verified
- **THEN** ready 清单 SHALL 绑定新源码哈希，后继 SHALL 继续原资源和输入核验后启动。
