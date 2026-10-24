# retired-tail-prefix-surface Specification

## Purpose
约束退役 Tail-SID／TIGER 前缀分析链路退出可执行面，同时保持正式生成和公共 writer 兼容。
## Requirements
### Requirement: Retired analysis pipelines SHALL be absent

可执行源码、配置与根脚本 SHALL 不再暴露 Tail-SID、TIGER prefix trace、prefix allocation probe 及其专用数据和产物读取实现。

#### Scenario: Inspect executable surface
- **WHEN** 扫描源码 import、Hydra targets 和根脚本
- **THEN** 三条退役链路及专用模块均不存在，历史证据保持原身份

### Requirement: Formal generation and shared writers SHALL remain compatible

六种正式方法及 BARS 当前 M3 SHALL 保留。TIGER SHALL 保持普通 beam 输出与严格 checkpoint 恢复；公共 auxiliary writer SHALL 使用调用方显式 validator。

#### Scenario: Restore formal TIGER
- **WHEN** 使用相同小型模型参数和输入运行普通 beam
- **THEN** 参数键、生成 SID 和累计分数与删除前完全相同

#### Scenario: Write LIGER path payload
- **WHEN** LIGER 为 auxiliary writer 传入其 path validator
- **THEN** writer 继续合并与校验该 schema，不导入退役 TIGER schema
