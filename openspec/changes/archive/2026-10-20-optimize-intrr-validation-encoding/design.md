## Context

`eval_step` 先调用 losses，再调用 generate，两者各自 encode_history。Lightning 验证使用 eval 模式，历史状态和 alignment loss 可在同一个 batch 中复用。

## Goals / Non-Goals

目标：一次编码产生原有全部评估输出。范围外：训练计算、RAN STE、beam 剪枝策略、超参数和跨 batch 缓存。

## Decisions

提取接收 user_state 的私有 loss 与生成方法，原公共方法仍编码后委托。eval_step 编码一次后调用两个私有方法。复用仅限栈内局部张量，避免缓存失效、checkpoint 和设备迁移问题。

以独立模型副本的原公共 losses + generate 组合构造旧路径参照，比较 loss、alignment、SID loss、排序 SID、分数与 labels；hook backbone 记录编码次数。覆盖 dropout 配置在 eval 下关闭、窄树和普通树。

## Risks / Trade-offs

GPU 争用仍可决定实际速度；本变更仅证明重复历史编码被消除。不以训练模式的 eval_step 随机 dropout 行为作为等价定义，正式验证必须使用 eval 模式。
