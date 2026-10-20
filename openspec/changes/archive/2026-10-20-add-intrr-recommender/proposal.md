## Why

RAN 核心已独立实现并验证，现需将其接入当前框架，构成可训练、可评价、可恢复的 IntRR。用户已确认通用协议以 TIGER 为参照；本模块只改变模型机制及所必需的数据表示适配。

## What Changes

- 在完整 TIGER 预处理末端将完整历史 SID 组映射为目录 compact UID，复用同一目标、采样、截断和 batch 容器。
- 实现作者 causal T5Stack、多层 FF、UID→共享 RAN→一商品一 token→用户状态→同一 RAN 的链路。
- 实现逐层推荐 CE 和历史 SID alignment，按出现位置加权；alignment 默认 0.1，明确公开 YAML 为 0.0 的差异。
- 原生合法 SID beam 累加路径 log probability，输出 `[B,10,H]`，复用 TIGER metrics 和公共 ModelOutput。
- 加入目录/结构 checkpoint 身份验证与小张量 CPU 测试。
- 本提案不包含实验配置与启动脚本；下一模块单独提案。

## Capabilities

### New Capabilities

- `intrr-recommender`: TIGER 数据协议上的 IntRR 推荐模型与监督、生成、恢复接口。

### Modified Capabilities

无。

## Impact

新增 `src/data/components/intrr.py`、`src/recommendation/intrr/backbone.py` 和 `module.py` 及对应单测。复用公共 reader、datamodule、容器、metrics 和 writer，不修改既有基线、不增加依赖、不运行正式训练。
