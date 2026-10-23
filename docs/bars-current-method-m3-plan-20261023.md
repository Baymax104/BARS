# BARS 当前方法 M3：机制与匹配消融计划

日期：2026-10-23。协议：`bars-fixed-half-hybrid-m3-20261023-v1`。当前状态：`completed_independently_accepted`。三臂150k训练、各自首次own-best Testing、C固定模型诊断及正式冻结预测贡献均完成独立验收，当前结果3/3、剩余执行0。Full相对Shared／零残差的NDCG@10分别提高17.38%／26.26%，去唯一Catalog CE后相对Full下降77.03%；12项组件用户区间均为正，C支持固定Full的生成／同池排序用途及正交互。按预定规则收口，追加实验和预算均0。

完整指标、12项组件区间及贡献分解、C四臂和边界见[当前M3结果](bars-current-method-m3-results-20261023.md)及[最终回执](evidence/bars-current-method-m3-test-20261023/README.md)；[训练审计](evidence/bars-current-method-m3-test-20261023/training-audit.json)、[Testing审计](evidence/bars-current-method-m3-test-20261023/independent-testing-audit.json)、[贡献审计](evidence/bars-current-method-m3-test-20261023/independent-contributions-audit.json)和[C审计](evidence/bars-current-method-m3-test-20261023/mechanism-audit.json)分别验收。下方矩阵和决定规则保持预定含义；02:37提交及02:39启动记录保留原时点，五份修改前文档的[before-testing](evidence/bars-current-method-m3-test-20261023/before-testing/manifest.json)不覆盖。本轮不改论文，不扩seed／扫描；区间不解释为训练seed稳健性。

[Linear最终回读](evidence/bars-current-method-m3-test-20261023/linear-final-readback.json)已于13:37:51核实当前五项全部Done、M3里程碑100%，原子项父关系及M2父项／九格Done保持。

用户要求按当前方法重新进行机制与消融实验并回退 Linear M3，已明确沿用 Beauty／training seed42。本轮据此提交下列有界队列；Testing 保持独立门禁，不自动排队或执行。范围调整须更新本计划及累计预算，不能将其他数据集或 seed 自动加入队列。当前 M2 九格结果、旧 M3 事实和已经发生的成本保持各自账本。

## 阶段问题与证据边界

本阶段回答：在固定内容向量和 SID、固定 alpha=0.5、SID CE＋Catalog CE 的当前 BARS 中，商品行为适配、角色独立残差、直接商品判别目标，以及目录相关性在生成和排序中的用途，分别获得什么支持。

当前 Full 已完成三数据集×三 seed 的 hybrid Validation 选点和正式 Testing，见[当前主矩阵结果](bars-hybrid-m2-results-20261023.md)。完整系统效果已有来源；当前模型的匹配组件和固定模型干预仍缺结果。论文现有组件研究正好包含 Shared、双侧零残差及去直接 Catalog CE，本阶段填补这三项已有不确定性，不增加新方法或新问题。

旧 M3 使用 learned alpha、三损失及 dense Validation：A 的 Full 为 `g953gzcq → e4a3b038`，B 的去 CE 为 `ec98cca4 → 0474e89a`、loss1/0/1，C 固定旧 Full、alpha约0.993415。旧 Shared 和共同零残差也来自旧训练目标及选点协议。它们保留[原计划](bars-untied-mechanism-plan-20261019.md)、[原结论](bars-untied-mechanism-results-20261019.md)和预算，不能补填当前条件；旧零残差等价审计不免除本轮重训。

相关工作定位沿用[当前研究范围和方法决定](../../research/docs/bars-fixed-half-no-mixture-main-20261021.md)：完整方法以 LIGER hybrid 等利用商品内容的生成式推荐为主要比较对象，TIGER 是基础架构对照，Shared 是内部表示对照。本阶段验证当前设计及推理链路，不把单个成熟组件表述为首创，也不以组件相似性扩展训练矩阵。

## 固定 Full 来源

只复用已验收的 Beauty／seed42 当前 Full，不重复训练或推荐 Testing。

| 字段 | 固定值 |
| --- | --- |
| variant | `untied_fixed_alpha_half_no_mixture` |
| train／Test | `httwyhka`／`prt5r0v5` |
| 自身首次最高 hybrid Validation | step46000，完成50k训练及100次Validation后验收 |
| checkpoint URI | `wandb://baymaxam/GRID/httwyhka?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=046000.ckpt` |
| checkpoint SHA256 | `f2ffd7939483c4e16fa9359a2a856865386d0823d6285321c53df1f1391ca4c9` |
| 预测 URI | `wandb://baymaxam/GRID/prt5r0v5?role=recommendation_output&alias=v0&file=merged_predictions_tensor.pt` |
| 预测 SHA256 | `7bd54d23e33b6b89b4d7de568f030172819293417fd5f74a4fc39a5ca1097065` |
| 用户及主指标 | 22,363用户，NDCG@10=0.04527919376226318 |
| 独立来源 | [Testing审计](evidence/bars-hybrid-m2-test-20261023/testing-audit.json)及[训练审计](evidence/bars-hybrid-m2-test-20261023/training-audit.json) |

## 最小实验矩阵与累计预算

三条新训练臂分别单独计数；不是把大型矩阵折算为一个实验。三组研究任务承接原 A／B／C 的问题分工。

| 组别与任务 | 条件 | 新训练 | 后续计划与当前状态 |
| --- | --- | ---: | --- |
| A／BMX-206：商品适配与角色表示 | `shared_fixed_alpha_half_no_mixture`；一张残差表，loss1/1/0 | 已完成1×50k | 自身best47500，Testing `e0m3cdsi` 和贡献均独立验收 |
| A／BMX-206：商品适配与角色表示 | `no_residual_fixed_alpha_half_no_mixture`；双侧有效残差恒零并冻结，loss1/1/0 | 已完成1×50k | 自身best43500，Testing `1ipsthvi` 和贡献均独立验收 |
| B／BMX-207：直接目录监督 | `untied_fixed_alpha_half_no_joint_ce_no_mixture`；双表独立，loss1/0/0 | 已完成1×50k | 自身best45500，Testing `srta7ooi` 和贡献均独立验收 |
| C／BMX-208：生成与排序用途 | 当前 Full，生成(.5／0)×排序(catalog／合法decoder完整SID logP) | 0 | `gkwknl0l` finished／exit0，production和全部预定统计独立验收通过 |
| A及B贡献 | 当前 Full及三个真实新对照的冻结预测 | 0 | `6cpl285w` 完成，4来源／12区间／24类别及贡献守恒独立验收 |

本阶段新增训练预算固定为3×50k＝150,000 optimizer updates，现已全部完成并独立审计；Full复用不再次计费。三个训练各100次hybrid Validation属于训练预算。用户本轮后续指令另行授权的3次各自身own-best Testing、一次冻结预测贡献和C一次固定模型诊断全部独立验收；本轮新增训练0、重试0、剩余执行0，追加实验及预算0。历史 M3 此前700k＋旧阶段50k＝750k，以及 M2 和其他阶段独立成本保持，不合并为本轮新增消耗，不逐轮重置预算。

不加入其他 seed／数据集、alpha或beam扫描、learned gate、额外 no_mixture、去 SID CE、上游重跑、独立 Validation、默认 smoke 或自动重试。失败保留实际消耗；修复有效性问题不自动增加重跑预算。

## 三组问题、预测与决定

| 组别 | 待减少的不确定性与预定预测 | 正向结果 | 负向或不确定结果 |
| --- | --- | --- | --- |
| A：Full／双侧零残差／Shared | Full相对零残差的NDCG@10为正；Full相对Shared评价当前角色表示选择 | 主指标配对区间全正时，保留对应固定训练来源的质量增益主张 | Full较差则收缩对应设计优越性；区间跨零记不确定，不写等价，不自动扩seed。Shared比较同时改变容量、共享约束和梯度耦合，不唯一归因梯度冲突 |
| B：Full／去直接Catalog CE | 当前直接商品判别目标具有净贡献，Full−noCE的NDCG@10为正 | 区间全正时，支持该目标在当前两损失设计下的作用 | 不支持时收缩其效果主张；去CE结果不用于声称存在替代mixture监督，不自动调权重维持叙事 |
| C：固定Full四臂 | 固定目录排序时，production生成相对alpha0改善覆盖／NDCG；固定生产候选池时，目录排序相对decoder评分有益 | 分别保留生成用途、同池排序用途及真实交互方向 | 分别报告无支持或损失，收缩对应链路主张；不把候选覆盖改善等同于最终指标改善，不预设正交互或其必要性 |

主指标为NDCG@10，辅助Recall@5、NDCG@5、Recall@10；全体预定方向均记录。固定模型干预、重训移除、表示约束对照分别解释，差值不相加为总收益分解。阶段到达150k或预定完成条件即判断，不通过改问题、改成功标准或换名称续预算。

去CE在当前1/0/0下仅保留SID CE，目录专属残差没有有效任务梯度；从零初始化并核验保持零。它回答移除直接目录目标后的系统变化。实现若保留零系数计算图以对齐DDP／Adam恢复，只是执行契约，不代表额外监督。共享内容投影仍可由SID路径更新，因此不将该臂概括为所有目录表示完全固定。

## 训练、选点与正式结果门禁

1. 固定Beauty三split、目录顺序、seen-mask、内容与SID输入。语义ID为 `dq77e3wo:v0`，digest `19ace08283163fbe687287fbacaa3842`；内容为 `3jtt9mpa:v5`，digest `ab56af975eac589c27eed6094482cbd7`。执行前逐文件复核输入和来源，不因路径相同跳过核验。
2. 三臂均scratch，`ckpt_path=null`，seed42、DDP2／global256／FP32／50k。沿用当前Full配方：AdamW base／residual LR0.0003／0.002、wd0.035、warmup2500／cosine50000、clip1。零残差参数冻结且不进入optimizer；其他臂参数与状态按各自身份校验。
3. 固定alpha0.5，每500更新执行hybrid Validation，共100次：概率混合beam20、全部cold并集、目录logits按catalog-row稳定Top10、无历史排除。每臂取自身首次最高val/NDCG@10；不能用Full best、last或旧dense来源替代。
4. 统一使用根脚本 `copmrec_ablation_train.sh`／`copmrec_ablation_inference.sh` 和 `src.main`，保留notes、显式dry-run及额外Hydra override。三变体、当前协议及真实loss/alpha/选择条件必须进入resolved config和W&B Config。
5. 提交远端前完成聚焦CPU验证、Hydra compose、脚本参数和语法检查；从仓库根目录执行Mutagen flush，三个session均Watching且无conflict后才提交独立tmux。只记录实际启动、排队和完成，不把准备完成视为训练或结果完成。
6. 训练完审计50k、100次非空hybrid Validation、finished／exit0、首次自身best、不变URI/SHA、模型及优化器身份。训练完成只解除Testing来源门禁；还须用户后续独立授权，才执行各一次own-best Testing。失败停止，不自动重试或换checkpoint。
7. Testing后核对22,363用户、真实key/标签、标准keys/predictions bundle、合法唯一Top10、checkpoint与上游lineage及产物哈希。独立从原始TFRecord复算四指标，再核验W&B summary；结果方向不决定审计是否通过。以上齐全才将该臂结果标Done。

## 固定模型四臂与配对分析

| 生成 | 最终目录logits | 最终合法decoder路径logP |
| --- | --- | --- |
| 当前production alpha0.5 | 正式生产复现臂 | 同production候选池的排序干预 |
| alpha0合法decoder | 固定目录ranker的生成干预 | 两阶段decoder参考 |

每batch分别搜索两次beam20；各生成池并入全部cold并去重，再用两种ranker对同一池评分。cold也计算合法decoder完整路径分数，不用beam顺序替代。真实目标只用于评价，不影响候选、排序或超参数。production＋目录臂必须逐用户精确复现 `prt5r0v5`，用户集、checkpoint/预测SHA和来源匹配；失败先修复有效性，不解释机制。

记录纯beam target coverage@20、并集coverage、候选数、目标rank、四项最终指标与dense辅助参考；给出固定ranker的生成差、固定池的排序差、生产联合差及生成×排序交互。dense只作固定模型参考，不新增独立dense Testing，不由结果自动提出hybrid优于dense或效率结论。

所有比较按真实用户key配对，PCG64／seed42／2000次共享用户重采样／95% pointwise区间；四臂共享每次索引，完整保留负向与跨零区间，不作训练seed稳健性解释。命中贡献按全体用户均值登记新增命中、丢失命中、共同命中排名变化，并核验三项精确加和为总差。当前Shared、零残差、noCE预测URI/SHA尚不存在，贡献入口须拒绝用旧对照默认填值。

## Linear与02:37提交／02:39启动历史登记

已复用[BMX-205](https://linear.app/baymax104/issue/BMX-205)总汇、[BMX-194](https://linear.app/baymax104/issue/BMX-194)实现和来源门禁、[BMX-206](https://linear.app/baymax104/issue/BMX-206)A两臂及贡献、[BMX-207](https://linear.app/baymax104/issue/BMX-207)B去CE、[BMX-208](https://linear.app/baymax104/issue/BMX-208)C四臂；旧100%完成状态已回退。启动前完整回读五项均Todo；启动核验后194仅实现准备Done，205／208为In Progress，206／207为Todo queued，正式结果仍0。旧描述、关系和完成记录已快照并保留历史区块。BMX-168、170至178及184共11个旧卡已退出项目和里程碑，保留原Done及父子关系；当前连接器没有issue删除接口，因此本次是退出当前列表，未物理删除。未删除W&B或checkpoint。见[Linear核验](evidence/bars-current-method-m3-20261023/linear-verification.json)及[执行回执](evidence/bars-current-method-m3-20261023/README.md)。

研究侧只维护[阶段说明](../../research/docs/bars-current-method-m3-20261023.md)和 `research-state.yaml` 当前指针，具体矩阵以本页为准。旧 `bars_untied_mechanism_20261019` 完整保留；本轮不改论文及其数值。

北京时间2026-10-23 02:37:07已在node1提交四个独立tmux，单槽按C→Shared→Zero→noCE顺序串行；C物理GPU4，三训练物理GPU4/5、DDP2。远端batch为 `/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m3_current_20261023_023410`。02:37:53的首次初始化查询尚无W&B run；02:39:00已核实C `gkwknl0l`为running、group=`mechanism_main`、当前协议/URI/alpha/hybrid config正确，source origin与四项上游lineage齐全。三训练仍queued、未实际更新，预留ID尚不等同于已有实际W&B训练。

| 任务 | run身份 | tmux |
| --- | --- | --- |
| C generation | 实际 `gkwknl0l`，running已核验 | `bmx-208-m3-generation-20261023_023410` |
| Shared | 预留 `gu3l2s2s`，queued | `bmx-206-m3-shared-20261023_023410` |
| Zero | 预留 `1k2ebqaw`，queued | `bmx-206-m3-zero-20261023_023410` |
| noCE | 预留 `7u93dubs`，queued | `bmx-207-m3-noce-20261023_023410` |

源码323份、525份Beauty TFRecord、四组脚本compose和C checkpoint／预测预检通过；本地133项通过、1项Windows Gloo跳过，node1实际2rank三臂CPU检查全部通过。提交不能证明实际模型forward、50k或机制完成；训练及正式结果仍0/3，Testing计划3／授权0／提交0／完成0，冻结预测分析等待新结果。完整来源及最新启动核验见[本轮回执](evidence/bars-current-method-m3-20261023/README.md)。
