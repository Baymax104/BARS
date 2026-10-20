## Why

IntRR 的验证每个 batch 分别为 loss 和 beam 生成调用历史编码，重复执行 UID RAN、backbone 和 alignment loss。当前训练的验证耗时占比较高，先消除这一可验证的重复计算。

## What Changes

- 验证和 test_step 在 batch 内共享一次历史编码结果。
- 保持训练、公共生成接口、合法 beam、loss 定义和 checkpoint 契约。
- 以旧路径为参照验证所有输出逐元素一致，并断言编码次数为一次。

## Capabilities

### New Capabilities

- `intrr-evaluation-encoding-reuse`: 验证 batch 内复用历史状态且输出等价。

### Modified Capabilities

无。

## Impact

仅涉及 IntRR 推荐模块及其 CPU 单元测试。队列交接和版本配置在此模块验证完成后单独处理；不改变外部训练协议，不承诺消除 GPU 争用。
