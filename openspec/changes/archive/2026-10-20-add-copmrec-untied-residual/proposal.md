## Why

BARS 已有无残差重训与固定 Full 的历史/目录两侧干预，但尚无共享残差相对两侧独立学习的重训对照。新增 Untied 条件，直接检验同一商品行为残差同时用于历史编码和目录评分的设计价值。

## What Changes

- 增加 `untied_residual` 训练/推理变体：保留共享内容投影，仅拆分同维、零初始化、独立优化的历史和目录残差，cold 两侧恒零。
- 两张表均进入原残差学习率组，保留三目标、learned alpha、50k scratch、dense Validation own-best 和 hybrid Testing 协议。
- 为新臂提供独立参数共享与 checkpoint 身份，保持 Full、原三臂和 fixed_alpha_one 的已有 checkpoint 兼容，原四 bundle 诊断范围不变。
- 仅准备 Beauty seed42 一个新增训练单元，复用已有 Shared Full；计划为一次50k训练和一次自身单卡hybrid Testing。本轮实现与本地验证，不启动正式实验或自动增加预算。

## Capabilities

### New Capabilities

- `copmrec-untied-residual`: 历史/目录双残差、匹配初始化与优化、严格来源隔离和有界实验准备。

### Modified Capabilities

- `copmrec-v2-formal-surface`: 现有消融入口支持额外 Untied 对照，原三臂及四 bundle 诊断保持固定。

## Impact

涉及 LIGER 历史残差调用接缝、CoPMRec 残差参数集合与严格恢复、消融配置及现有根脚本、CPU 小模型测试和研究计划。复用统一 `src.main` 入口和共享 writer，不增加依赖。独立表的残差参数由128N增加至256N，完整报告容量差异；不以该对照唯一归因收益机制。
