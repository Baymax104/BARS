## Context

当前正式 v2 主损失实现在 `catalog.py`，通过共同的目录 logits 同时计算完整目录 CE 与合法 SID 前缀 mass。`mixture.py` 使用零初始化的全局 gate logit，默认可学习；`ablation.py` 提供原三臂及严格来源校验。最终部署为 dense 商品排序，不使用混合权重。

## Goals / Non-Goals

目标：在相同初始化、数据、三目标配置和训练日程下，准确实现 alpha=1 的训练对照，保持旧 checkpoint 可恢复，并提供可手动执行与核验的计划。

范围：仅增加 Beauty seed42 一个训练臂及其 Testing。无固定 alpha 扫描、额外 seed/数据集、Full 重训或旧实验重新标记。原三臂四 bundle 的机制分析保持原定义。

## Decisions

1. 沿用 `copmrec_ablation_train/inference` 与 `--variant fixed_alpha_one`。扩展训练允许集合，保留原 `VARIANTS` 三臂集合供已有诊断使用，避免改变四 bundle 统计协议。
2. 抽取有效混合概率和有效 alpha 的小接口：learned 继续使用原 log-space 混合；固定端点直接返回目标 content log probability。冻结零初始化 gate 并由原参数过滤排除优化，避免无穷 logit、近似端点和 RNG 变化。
3. 新臂保留 SID CE + joint CE + mixture NLL 三项权重1。在唯一完整 SID 且同一 logits/支持集时，验证 mixture NLL = joint CE / H，连同梯度与 S+(1+1/H)J 对齐。
4. 在 ablation 和顶层 checkpoint 记录 frozen_1、固定值1.0及独立 variant；拒绝错误臂或伪造端点状态，Full 与旧三臂字段和值保持兼容。
5. 复用 BMX-120 的 Full：训练 rmgfscr0 / Testing 57jvuy59。新臂独立 scratch 50k、DDP2、global256、FP32、warmup2500，每500步 raw val/ndcg@10 首次最优选点，随后自身 checkpoint 单卡 Testing。
6. 研究状态单独登记本次增补，原450k主矩阵与150k消融完成成本保留，增补计划总计650k；创建独立 Linear 待执行任务。完整运行由用户手动启动。

## Risks / Trade-offs

- 概率数值与端点梯度可能偏离 CE 等式 → 用最小内存目录验证等式、梯度、所有可训练参数 finite，以及精确 alpha 日志。
- 新臂来源可能与 Full 混用 → 严格 checkpoint 契约、自身恢复和双向错臂拒绝测试；Testing 要求自身 URI/SHA256。
- alpha=1 同时移除生成分支参与及混合权重学习 → 结果只解释当前 learned mixture 与 pure mass 的训练差异，不能唯一归因于可学习性；跨零区间不解释为等价。
- 原四 bundle 分析被扩展集合意外改变 → 保留三臂集合，回归测试原诊断路径。

## Migration Plan

本地通过聚焦 CPU 测试、Hydra compose、脚本参数与 OpenSpec strict 后，报告实现与计划就绪。用户实际运行前通过仓库同步入口 flush 验证；本次不自动同步或启动。回退可删除本次新增臂和计划记录，旧实验配置与产物不迁移。

## Open Questions

效果及训练成本待用户执行后登记。当前无阻断实现的问题。
