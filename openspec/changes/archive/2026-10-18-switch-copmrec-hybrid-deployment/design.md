## Context

CoPMRec 已完成正式 v2 训练，checkpoint 中的 `copmrec_unified_scratch`、formal release、optimizer 和 scheduler 身份均严格校验。该训练契约含历史 dense deployment 描述；改变字典会拒绝全部已有 own-best。LIGER 已实现生成、cold 并入和稳定候选重排，CoPMRec 已有按具体变体分派的候选概率 processor。

## Goals / Non-Goals

**Goals:** 默认 hybrid20 推理、显式 dense 辅助模式、dense Validation 不变，严格复用已训 own-best 并发布独立部署身份。正式执行范围为 13 次推理及 1 次 hits 分析。

**Non-Goals:** 不新增训练，不改 checkpoint 字节或训练来源，不引入新的最终混合评分，不把部署统一表述为效率贡献，不把单数据集单 seed 临时结果替代主矩阵。

## Decisions

1. **训练身份与部署分离。** 保留 `unified_scratch_contract` 和 `formal_release` 的原始内容及严格比较；新增只描述本次运行的 `deployment_contract` 属性和产物元信息。另一种做法是重写旧 deployment 字段，但会污染已完成训练身份并破坏恢复，因此不用。
2. **复用检索路径。** `CoPMRec.retrieve` 显式接受 hybrid/dense，并调用 `Liger.retrieve`；保留 `self.candidate_processor` 动态分派。hybrid 仍使用20条 beam、全部 cold、去重和 joint catalog logits 稳定重排。显式 dense 使用全部目录。
3. **继续 dense 选优。** `eval_step` 保持显式 dense，与 LIGER 的 dense Validation/hybrid Testing 一致。原 checkpoint 选点不重新搜索，不使用 Testing 选择参数。
4. **记录有效候选策略。** Full/no_residual/no_joint_ce 来源为 checkpoint 学得的 alpha；no_mixture 记录冻结 0.5；fixed_alpha_one 记录精确1并使用无 gate 的 processor。构造器兼容字段0.5不能冒充 Full 实际 alpha。
5. **分析按产物协议区分。** hits 读取四份新 hybrid bundle 并校验部署身份；residual 的原全目录 V11 复现规则保留 dense 身份。标准预测继续为 keyed `keys/predictions`，不改共享 writer 协议。

## Risks / Trade-offs

- [旧 checkpoint 不能恢复] → 原字典及严格检查保持不变，增加跨部署恢复单测，同时拒绝篡改的旧身份。
- [模式和元信息不一致] → 配置从实际 model prediction mode 生成独立部署与 eligibility 元信息；显式 dense override 同步改变标签。
- [把 no_mixture 当成单一训练干预] → hybrid 下它同时失去 mixture 目标和候选 gate 学习，主消融采用完整条件比较，不声称纯目标因果。
- [有限 beam 被误认为精确 dense] → 保留实际候选子集语义和非法/重复候选测试；alpha1 的路径概率等价不保证有限 beam 检索等价。
- [效率被过度表述] → 当前仍计算全目录 logits/prefix mass，不提出性能改善主张。

## Migration Plan

完成 CPU 单测、配置 compose、脚本检查和 OpenSpec strict；由主执行者 flush 三个 Mutagen session 后使用统一入口在 node1 tmux 串行/有界运行13次推理及1次 hits，核验完成状态和 keyed 产物，再更新研究状态与 Linear。显式 dense 模式保留旧辅助结果复现能力；实现完成与实验完成分别登记。
