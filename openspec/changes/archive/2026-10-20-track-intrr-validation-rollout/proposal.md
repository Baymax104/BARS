## Why

已完成模型模块的验证复用优化，需要让后继正式单元可追溯到新实现，同时等当前训练自然结束后再切换。原队列 guard 固定旧源码哈希，直接同步会阻断后继。

## What Changes

- 在训练 experiment 中增加验证实现版本元数据。
- 原训练完成且退出 0 后通过既有 Mutagen 入口同步，核验来源，再放行队列。
- 保留原 preflight 和首格来源，单独保存新版本交接证据。

## Capabilities

### New Capabilities

- `intrr-validation-rollout`: 等待前驱结束的显式版本交接和可追溯配置。

### Modified Capabilities

无。

## Impact

仅 IntRR train experiment 元数据、配置验证和现有队列的运行记录。沿用七格队列、W&B ID、50k 预算及资源等待规则。
