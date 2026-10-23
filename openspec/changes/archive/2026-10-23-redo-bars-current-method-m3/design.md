## Context

当前 Full 为 `untied_fixed_alpha_half_no_mixture`，Beauty42来源 `httwyhka` own-best46000及正式预测 `prt5r0v5`。旧 M3 使用另一训练目标与选点协议；新阶段须独立记账并重训匹配对照。

## Goals / Non-Goals

目标：建立同一当前方法下的三条组件臂、固定模型四臂机制分析与可审计来源。保持旧配置显式复现能力，当前完成覆盖从零登记。

不新增 gate/alpha 扫描、训练seed或数据集，不改论文数值，不删 W&B 与 checkpoint。默认沿用 Beauty42 范围；范围答复到达后调整实际执行矩阵。

## Decisions

- 新增 `shared_fixed_alpha_half_no_mixture`、`no_residual_fixed_alpha_half_no_mixture`、`untied_fixed_alpha_half_no_joint_ce_no_mixture`，统一固定alpha0.5、hybrid选点；旧variant不改。
- 三个新臂使用协议 `bars-fixed-half-hybrid-m3-20261023-v1`，loss分别1/1/0、1/1/0、1/0/0，独立scratch50k/100val/own-first-best。
- 去CE臂通过零系数目录loss保留计算图连接，确保DDP和Adam同step恢复契约；catalog residual从零初始化且保持零。实际总目标仍为SID CE，不能解释为存在替代mixture监督。
- 机制诊断严格消费当前own-best与固定预测；当前生产条件命名production，历史learned来源保留其命名。两次beam搜索的各自同池排序，目录stable ties、全部cold和合法decoder归一化保持。
- 贡献入口要求显式当前对照URI/SHA；无新对照时拒绝把旧结果当作默认值。
- Linear原描述与关系先快照，当前计划置于顶部，旧完成记录保留历史区块；过时来源退出M3，当前跟踪重新从待执行开始。

## Risks / Trade-offs

- 去CE同时移除最后一个目录判别目标 → 明确其估计对象，并验证专属目录参数的零梯度与恢复。
- 固定alpha .5与旧learned命名混淆 → 当前元数据显式记录fixed/0.5及新协议，旧显式来源保留原身份。
- 训练完成不等于结果可用 → 每臂单独登记50k/100val、own-best URI/SHA、Testing授权及独立复算；不自动Testing。
- 长训练不可用提交回执替代结果 → 启动后只报告实际启动/排队状态，直到完整验收才Done。
