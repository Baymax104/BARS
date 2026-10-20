## Context

当前 Untied Beauty42 train `g953gzcq`／Test `e4a3b038` 已完成，Shared、共同零残差及近邻 baseline 预测均已冻结。旧诊断中的 residual 屏蔽方法、dense V11 重现和 prefix 的 Full 判定都面向 Shared，直接替换来源会误判 Untied。用户本轮明确将机制验证置于多数据集／多 seed 扩展之前。

## Goals / Non-Goals

**Goals:** 将“商品级行为适配→目录监督→相关性参与生成和排序”拆成三个有界实验组，准备可运行入口、身份和匹配统计；以当前 Beauty42 为唯一数据单元。

**Non-Goals:** 不更换主方法、不增加模块、不扫描 alpha、不验证梯度冲突、效率或 cold 改善，不执行正式远端模型任务，不自动开始后移矩阵。

## Decisions

### 三个实验组及成本

1. **商品行为适配贡献：** 复用 Shared 与经审计的旧 `no_residual` hybrid 来源，与 Untied 直接比较。CPU 数值审计验证双表冻结零与旧零表在公共初值、dropout RNG、三 loss、公共 AdamW／scheduler 多步轨迹及预测上一致。已有预测的 keyed 用户配对、命中得失与共同命中排名贡献由独立 `Trainer.test` 分析输出，正式模型 forward 为 0。
2. **直接目录监督：** 新增 `untied_no_joint_ce`，只有 joint catalog CE 权重从 1 到 0；保留双表和其他设置。计划至多 1×50k scratch＋1次自身 raw dense validation-best hybrid Test，须用户另外启动；原 Shared 对照不改身份。
3. **固定 checkpoint 的生成／排序链路：** 同一次 `Trainer.test`，只对当前 Untied own-best，在生成 learned mixture／alpha0合法 decoder 两条件下分别生成 beam20，并入全部 cold，得到各自固定池；每池分别按目录评分／合法 decoder 完整 SID log probability 排序，构成预定 2×2。恰为两次自由生成和四组候选内排序，不增加训练或做参数搜索。

### 固定池与评分隔离

四臂均无历史排除、同一目录、cold union 和 stable catalog-row ties。decoder 分支在同一合法支持上归一化；对候选的路径分数通过完整 encoder states 的 teacher forcing 计算，候选来自模型及目录，与真实目标无关。候选评分分块执行，避免复制整批候选的编码状态。目标标签只用于覆盖、rank、hit 和 NDCG 的测量。

记录纯 beam target coverage、union coverage、pool size、dense rank/reference、每臂 Top10 与四指标。learned＋catalog 臂必须逐用户精确复现冻结 `e4a3b038` 产物；否则整组无效。生成对比固定最终 ranker，排序对比固定池；报告配对差与生成×排序交互，但不称重训收益。

### 独立能力与严格身份

新分析模块和 experiment 不放宽正式 retrieve 的 trace 限制。backbone 只能为 `untied_residual`，使用已有 checkpoint loader 的 SHA 校验，再调用完整契约与严格 state restore；Shared／缺表／错误 seed／错误来源应拒绝。输出通过 `StructuredAnalysisOutput` 与公共 writer；JSON／CSV／keyed bundle 由 `paths.output_dir` 管理，W&B 配置记录结构化条件。

既有 `no_residual` 复用不改写 checkpoint。新 `untied_no_joint_ce` 的 variant、loss、双表与恢复身份独立，旧所有 variant 的契约必须逐项保持。

### 统计与判定

主指标 NDCG@10，辅助 R@5／N@5／R@10；真实用户配对 PCG64 seed42、2000次、95% pointwise percentile CI，同抽样复用四指标。命中得失和共同命中排名贡献必须加和为观察到的总差。用户 bootstrap 不估计训练 seed 不确定性；固定模型干预与重训移除分别解释。

正向则保留对应局部机制主张；负向或区间跨零则收缩相应归因，保留完整方法真实效果，不扩参数扫描、seed 或模块。生产复现或来源失败先修复有效性，不作为机制反证。

## Risks / Trade-offs

- [旧零表复用被误读为新 run] → 保存原来源、数值等价条件及已完成成本，明确属于共同退化对照。
- [decoder 对 cold 分数缺失引入候选差异] → 对同池所有合法候选计算完整路径概率，不用 beam 顺序或负无穷占位替代。
- [概率连接退化或学得 gate 近端点] → 不要求 learned gate 独立贡献，也不把固定条件结果推广为普遍必要性。
- [准备完成被误写为实验完成] → Linear 分开实现验收与执行任务，所有新 run ID 为 null；保留手动启动门禁。

## Migration Plan

实现并验证独立入口后，先登记机制阶段的准备状态与后移矩阵，再由用户明确启动相应诊断和唯一新训练臂。当前普通入口及已有结果不迁移。回退时停止使用新 experiment 即可，无既有数据或 checkpoint 修改。

## Open Questions

机制结果由预定实验决定；本轮不填写未来结果。共同零表结构等价的 CPU 审计不声称重放原 DDP 全训练轨迹。
