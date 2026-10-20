## Why

用户要求在当前框架新增 IntRR 比较基线。先独立实现作者共享 Recursive-Assignment Network（RAN），核准递归分配、STE 和 teacher forcing，避免在整体接入后才发现核心机制偏离。

## What Changes

- 固定作者实现来源 `DreamX-Rec/IntRR@806e0f1969ed61a0748902649b335c0ea066de00`，引入独立 RAN 核心。
- 实现共享可训练 codebooks、层间 MLP、商品侧 hard-forward/soft-backward 分配和用户侧目标前缀 teacher forcing。
- 用最小 CPU 输入验证数学输出、监督路径、梯度及无效输入。
- 本提案仅覆盖 RAN 核心；数据/Lightning 接入与实验配置分别在后续提案实施。

## Capabilities

### New Capabilities

- `intrr-ran-core`: 忠实于作者公开实现的递归分配与 SID 监督核心。

### Modified Capabilities

无。

## Impact

新增 `src/recommendation/intrr/` 内的核心模块和 CPU 单测，不改变既有基线，不增加依赖，不启动训练。后续接入遵守用户确认的 TIGER 通用协议。
