# BARS Untied Beauty42 机制链路与贡献验证

日期：2026-10-19。用户首先在当前 Untied Beauty／seed42 上验证论文机制；此页保留 M3 的预定设计并登记完成情况。多数据集、多 seed 在本阶段立项时后移，之后用户已另行授权 M2 八格训练并提交；其当前状态以[研究执行计划](../../research/ideas/current-plan.md)为准。[原主矩阵计划](../../research/docs/copmrec-untied-main-method-plan-20261019.md)保留原设计与来源，矩阵成本不并入本页机制预算。

## 阶段问题与固定范围

待检验的链路为：**商品级行为适配 → 直接目录监督 → 目录相关性参与候选生成与最终排序**。评价分别回答行为参数是否有用、直接商品 CE 是否有额外作用、所学相关性在推理两阶段如何发挥作用。完整方法贡献、重训移除与固定 checkpoint 干预分开解释。

唯一数据单元为 Beauty／training seed42；固定内容、RKMeans SID、数据分片和目录，主指标 NDCG@10，辅助 R@5／N@5／R@10。保留所有预定条件和方向，不按 Testing 改 checkpoint、阈值或候选数，不增加训练 seed、alpha 扫描、梯度冲突或新模块。

用户已明确授权同步 node1 并用 tmux 启动本阶段三组机制实验。三组显式 dry-run 均 exit0，正式会话来源／配置启动核验通过；A、B、C均已完成且独立产物验收通过，M3机制阶段完成，追加机制实验与训练预算均为0。代码不切换根默认模型，不改已有 run／Artifact／Done。阶段结论汇总见[机制结果分析](bars-untied-mechanism-results-20261019.md)。

本次运行标签为 `20261019_040701`，来源与资源见[启动 spec](evidence/bars-untied-mechanism-launch-20261019/spec.json)，实际 argv、tmux 和 wrapper 指纹见[正式提交回执](evidence/bars-untied-mechanism-launch-20261019/formal_launch.stdout.txt)。

| 组别 | 正式 run | 资源 | tmux | 当前登记 |
| --- | --- | --- | --- | --- |
| A／BMX-206 | `84a07f71` | CPU | `bmx-206-bars-20261019_040701` | finished／exit0，独立验收通过 |
| B／BMX-207 | train `ec98cca4`／Test `0474e89a`／贡献 `3e62b44e` | GPU0、1／DDP2；Test单卡；贡献CPU | `bmx-207-bars-20261019_040701` | 50k／100val／自身best49000，Test与贡献均finished／exit0，独立验收通过 |
| C／BMX-208 | `1241f8aa` | GPU2 | `bmx-208-bars-20261019_040701` | finished／exit0，production逐用户Top10精确复现，独立产物验收通过 |

## 当前已完成证据与尚未回答的问题

| 证据组 | 已完成事实 | 对本阶段的作用 |
| --- | --- | --- |
| Untied Beauty42 完整方法 | train `g953gzcq`，own-best39500，Test `e4a3b038`，N10=0.04546932472；对 LIGER／LETTER 四指标直接配对区间为正 | 当前完整方法效果已获支持；本阶段聚焦设计及链路作用 |
| Untied／Shared | Shared Test `64mjlgze`，N10=0.03967023631；Untied N10相对+14.6182%，四指标用户区间支持当前选择 | 角色独立的直接匹配证据；容量、约束及梯度耦合共同变化，不单独识别梯度冲突 |
| Shared 三数据集三 seed | 九格及有效 baseline 已完成 | 保留框架比较证据，不补填 Untied 格，不作为本阶段先行任务 |
| Shared 三移除 | no_residual／no_joint_ce／no_mixture 的 Beauty42 hybrid N10相对Full约−9.28%／−4.24%／−2.76% | no_residual 可按严格共同退化审计复用；其余非零 Shared 表不能冒充 Untied 臂；no_mixture还改变搜索alpha |
| Shared fixed alpha1 | 主 N10 用户区间跨零 | learned gate 的独立必要性不作为论文前提；本阶段不新增端点扫描 |
| Shared 残差2×2／正确前缀／hits | 已完成各自 dense、teacher-forced 或列表分析 | 不替代 Untied hybrid 的自由生成／排序干预；新分析修正具体证据缺口 |
| IntRR Beauty42 | train `oipt22mb`／Test `hhaubm7t`独立审计通过，Untied N10相对+49.7508% | 保留近邻完整方法比较；其余八格同样后移 |

阶段立项时的主要不确定性为：商品参数相对共同零残差的净贡献、直接目录 CE 对 Untied 的额外作用、目录相关性在候选覆盖与候选排序中的具体用途。完成证据支持商品行为适配贡献、直接目录CE的额外作用，以及固定当前模型时目录相关性在生成和排序中的用途与正交互。三组共同支持本页机制主线，范围为Beauty／seed42；已有共享与gate对照仍约束相应独立主张。

Linear父项为[BMX-205](https://linear.app/baymax104/issue/BMX-205)，实现与复用准备为[BMX-194](https://linear.app/baymax104/issue/BMX-194)。三个执行项依次为[A／BMX-206](https://linear.app/baymax104/issue/BMX-206)、[B／BMX-207](https://linear.app/baymax104/issue/BMX-207)、[C／BMX-208](https://linear.app/baymax104/issue/BMX-208)；提交会话不将实验标Done，结果须经完成审计。

## 三个预定实验组

### A：商品行为适配贡献——复用来源，零模型 forward

对照为当前 Untied、已完成 Shared、经算法等价审计的共同零残差，保持原身份：

| 条件 | train／Test | 自身最佳 | NDCG@10 来源值 |
| --- | --- | ---: | ---: |
| Untied 主方法 | `g953gzcq`／`e4a3b038` | 39500 | 0.04546932472217077 |
| Shared 对照 | `rmgfscr0`／`64mjlgze` | 47000 | 0.03967023631268397 |
| 共同零残差（原 no_residual） | `gtwv2c4n`／`xzfp1pgt` | 47000 | 0.035989463887354425 |

零残差复用要求：公共初值和构造 RNG 不变；两张零表冻结且不进 optimizer；公共参数顺序、AdamW／scheduler、dropout随机流、三loss及预测一致；真实训练50k／100val／exit0、固定上游及 hybrid 部署匹配。CPU 小模型多步回归验证算法条件，冻结记录核验真实来源；不声称重放原DDP全训练，不重贴旧variant。

正式分析通过 `experiment=bars_untied_contributions`、`Trainer.test` 仅读取冻结预测和真实标签。输出 reference−comparison 四指标、95%用户配对区间、Untied独有命中／对照独有命中／共同命中排名变化；三项NDCG贡献按全体用户平均，必须精确加和为总差。目标频次与长尾不是本组必需主张，不追加切片扫描。B完成后已通过同一接口添加其真实 URI／SHA，新增分析 `3e62b44e`，不修改A原产物。

成本：0训练、0新推荐推理、1次已有预测分析，0模型forward。正式分析 `84a07f71` 已完成并通过[独立验收](evidence/bars-untied-mechanism-launch-20261019/A-result-audit.json)：Untied−共同零残差N10为+0.00947986083（+26.3407%），95%用户配对区间[0.00716641349,0.01154454015]，四指标区间均正，命中贡献精确守恒；不替代B／C结论。

### B：直接目录监督——唯一新训练臂

新增 `variant=untied_no_joint_ce`：保留独立历史／目录残差、共享P、learned全局alpha、SID CE和mixture NLL；仅移除joint catalog CE。mixture仍可给目录评分与双表传递梯度，因此该对照回答直接商品CE的额外作用，不称“完全移除目录监督”。

对照复用当前Untied own-best及正式Test；新臂独立scratch50k、同配方、100次raw dense Validation，取自身首次最高val/NDCG@10，再执行一次原hybrid部署Testing。DDP2/global256/FP32；主LR0.0003／双表残差LR0.002／wd0.035／warm2500／cosine50000。三split、内容／SID／目录／seen-mask指纹固定；新variant具有独立损失和完整恢复身份，拒绝跨臂或缺表。

成本：**已完成1×50k＋1次自身own-best Test**。训练 `ec98cca4` 在GPU0／1完成50k、100次Validation并exit0；自身首次最高 `val/ndcg@10` 对应step49000，checkpoint SHA256为 `075749c79484c0eb002a6801e11dbd25bc7dfddaf0040d717a34d3b7f7009885`。其 tmux wrapper 通过严格门禁后自动执行hybrid Test `0474e89a`，N10=0.0425214213906603，再执行零forward配对贡献分析 `3e62b44e`；两者均finished／exit0并通过[独立验收](evidence/bars-untied-mechanism-launch-20261019/B-test-result-audit.json)。Full−noCE N10为+0.00294790333（+6.93275%），95%用户配对区间[0.00183797073,0.00408401294]；四指标区间均正。N10的gain、loss、common-rank贡献分别为+0.00676821401、−0.00474177940、+0.00092146872，严格守恒。该对照支持当前固定训练seed下直接目录CE的额外作用，不将用户区间解释为训练seed稳健性。不得以旧 Shared `no_joint_ce`、last或其他臂checkpoint替代。保留门禁与续接配方：[own-best审计](evidence/bars-untied-mechanism-launch-20261019/posttrain_audit.py)、[自动续接](evidence/bars-untied-mechanism-launch-20261019/posttrain.py)。

### C：生成与排序链路——固定checkpoint 2×2

来源只用当前Untied own-best，权重与alpha不更新。一次 `experiment=bars_untied_mechanism` 的单进程 `Trainer.test` 包含以下四臂：

| 生成条件 | 最终目录评分 | 最终合法decoder路径logP |
| --- | --- | --- |
| checkpoint learned mixture | production对照：须精确复现`e4a3b038` | 同一learned候选池的排序干预 |
| alpha=0的合法decoder | 固定目录ranker的生成干预 | 两阶段decoder条件 |

每个生成条件实际执行一次beam20搜索，共两次搜索；对其合法候选并入全部cold、去重，并在**完全相同的池**上做两种排序。decoder路径分数在同一合法分支支持上归一化，对池中全部候选包括cold计算，按分块teacher forcing控制内存；不用未定义的cold分数或beam顺序替代。真实目标只用于评价，不参与搜索、候选添加或排序。

记录纯beam target coverage@20、并集coverage、候选数、target candidate rank、四项最终指标与同目录dense参考。生成差固定ranker，排序差固定候选池，另给生成×排序交互。用同一用户配对CI与命中贡献说明变化发生在哪一阶段；这不是重训消融，也不把teacher-forced候选评分本身称为自由生成成功。

有效性门禁：learned＋目录臂逐用户Top10必须精确复现冻结正式预测，用户集、ckpt SHA、双表、目录及部署元数据匹配；权重与gate不被修改；非法、重复、缺失用户和候选必须拒绝。复现失败先修复有效性，不解读机制结果。

成本：0训练，1次固定模型诊断遍历；每batch两次自由生成和候选分块评分，四个预定排序结果，无独立Validation、alpha扫描或额外checkpoint。正式诊断 `1241f8aa` 已finished／exit0并通过[C独立验收](evidence/bars-untied-mechanism-launch-20261019/C-result-audit.json)，production逐用户Top10精确复现冻结Full预测。固定catalog排序时learned−alpha0的N10为+0.013490634，95%用户区间[0.011630275,0.015288160]；同learned池catalog−decoder为+0.016025429，区间[0.014217583,0.017975144]；生成×排序交互为+0.007999078，区间[0.006005437,0.010024595]。纯beam目标覆盖从7.2844%提高至10.4861%，两条件加入cold均另覆盖138人。C保留原诊断float32逐用户值与其区间，不覆盖正式Full的double复算值；统计范围是固定训练来源的用户抽样，不是训练seed稳健性。四臂、全部预定对比与贡献见[机制结果分析](bars-untied-mechanism-results-20261019.md)。

## 结果如何改变叙事

| 问题 | 支持时保留的主张 | 负向／区间跨零／混合时的决定 |
| --- | --- | --- |
| A：商品残差净贡献 | 当前Beauty42推荐质量受益于商品级行为适配 | 收缩相应经验归因，保留真实完整方法比较；不从固定关闭的损失推算重训收益比例 |
| B：直接目录CE | 直接商品监督对当前Untied条件有额外作用 | 不独立强调额外质量增益，按真实结构描述训练目标；不扩权重扫描或seed |
| C：生成使用posterior | 固定当前模型时，目录相关性改善候选覆盖或最终推荐 | 若无稳定作用，收缩“生成阶段带来质量收益”的表述；连接的数学事实与实证用途分别陈述 |
| C：最终目录评分 | 同候选条件下目录评分改善排名／命中 | 记录目标与训练状态下的权衡，不声称整个两阶段都必要；不增加新ranker或重训策略 |

不要求每个组件独立显著或四臂全部取胜。若证据表明收益主要来自商品级评分，则论文围绕经支持的相关性建模价值组织；若完整方法或核心适配作用缺乏支持，按阶段预算收缩主张，不扩模块维持原故事。

## 账本与优先级

统一阶段协议：`bars-untied-mechanism-beauty42-20261019-v1`。M3账本为此前700k加本阶段已完成50k，累计750k，不含另行授权M2；本阶段正式训练完成数为1、正式Test完成数为1，均通过独立验收。A、B后续冻结预测贡献分析和C均不增加训练；三组均Done，本阶段完成，追加机制实验与训练预算均为0。三次显式 dry-run 均 exit0，仅作启动有效性验证，不作为正式研究结果。

BARS M2八格400k＋8Test与IntRR M4八格400k＋8Test保留原计划和来源。立项时两矩阵后移、相关未完成项移至Backlog并登记依赖；这是本阶段的启动顺序记录。之后用户已另行授权并提交M2八格训练，其实时状态以[研究执行计划](../../research/ideas/current-plan.md)为准，本页不调度或判定其完成状态。各账本独立，不把矩阵计入当前机制阶段50k预算，也不逐轮重置机制额度；本阶段原启动授权只覆盖上述机制实验。

实现提案：[OpenSpec归档](../openspec/changes/archive/2026-10-20-add-bars-untied-mechanism-study/proposal.md)。实现验证、冻结来源及参考命令保存在 `docs/evidence/bars-untied-mechanism-20261019/`；本次实际提交与后续运行回执保存在 `docs/evidence/bars-untied-mechanism-launch-20261019/`。
