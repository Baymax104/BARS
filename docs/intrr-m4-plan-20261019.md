# IntRR M4 实验计划

> 最终完成更新（2026-10-20）：Toys三seed各完成自身best全量Testing及独立验收，Beauty／Sports／Toys × seeds42／200／2026完整矩阵9/9完成。累计9训练／450k＋9Testing，剩余训练与Testing均0，训练重试0；原Beauty42复用，新增八格沿用原400k预算。逐格四指标、三seed均值与样本标准差及全部来源见[最终结果报告](intrr-m4-results-20261020.md)。下方6/9、3/9及最初计划保留历史时点含义。

> Sports执行更新（2026-10-20）：用户要求将已完成训练进行下一步。Sports42／200／2026均核准50k、500次验证、首次自身best及checkpoint身份后，各完成一次全量Testing并独立验收；Beauty与Sports共6/9格Done。Sports NDCG@10 mean±sample std为0.01439775±0.00063336（ddof=1），见[Sports三seed报告](intrr-sports-three-seed-results-20261020.md)。Toys42仍在GPU4/5训练，另两格排队，原训练与预算保持。下方3/9回执保留此前时点含义。

> 最新执行更新（2026-10-20）：用户要求训练完成后继续。Beauty200／2026已分别以自身best49,900／47,300完成一次全量Testing并独立验收，复用Beauty42后Beauty三seed Done，完整矩阵3/9。Sports／Toys六格此前在起训前因七份无关BARS配置导致全局source hash变化而停止；核准IntRR依赖不变、61项检查通过并保留失败记录后，原GPU4/5训练队列已恢复，Sports42训练、其余五格排队，无训练重试或额外训练格。Beauty结果与全部证据见[三seed报告](intrr-beauty-three-seed-results-20261020.md)；下方旧启动记录保留时点含义。

> 当前启动更新（2026-10-19）：BMX-205机制已Done，用户随后明确要求“在node1上启动intrr训练，使用tmux启动”，覆盖此前Backlog／Low暂停决定。剩余八格已提交独立tmux／GPU0/7串行DDP队列，当前Beauty200／BMX-197运行，其余七格等待前驱成功结束；父项BMX-195与首格为In Progress，其余为Todo。首格200步checkpoint／Adam更新、双rank与来源核验通过；本次仅训练，关闭自动Testing。Beauty42/BMX-196 Done与原预算保持。实际身份、启动核验及完整原始记录见[启动回执](evidence/intrr-m4-launch-20261019/README.md)。下文保留初始计划口径，实时执行状态以上述回执及研究状态为准。

更新日期：2026-10-19。用户要求将IntRR实验计划添加到Linear M4。本文件与M4父项及九个实验单元同步；本次登记不启动训练或Testing。

## 1. 目标与当前状态

补齐IntRR在Beauty／Sports／Toys × training seeds42／200／2026上的完整方法比较，缩小目前只有Beauty42结果的覆盖不确定性。采用当前已实现的IntRR，不新增机制或调参。当前覆盖1/9，Beauty42已完成并独立审计，其余8格Todo。用户本次要求登记Linear M4计划，未要求启动余下实验；不自动排队。

## 2. 已有依据与来源

作者公开实现、三个独立OpenSpec接入、152项聚焦测试、node1 dry-run／5step验证已完成；接入阶段临时产物已删除，正式产物保留。来源：GRID的 `docs/intrr.md`、`src/recommendation/intrr/SOURCE.md`、`configs/experiment/intrr_{train,inference}.yaml`、`configs/model/intrr.yaml`。
Beauty42训练 [oipt22mb](https://wandb.ai/baymaxam/GRID/runs/oipt22mb) 完成50k／500次验证，own-best49400，Testing [hhaubm7t](https://wandb.ai/baymaxam/GRID/runs/hhaubm7t) 覆盖22363用户；四指标独立重算与W&B最大误差3.5e-17。复用既有合规结果，不重跑。实证与完整审计：`docs/intrr-beauty42-results-20261019.md`、`docs/evidence/intrr-beauty42-test-20261019/testing-audit.json`。

## 3. 矩阵与冻结上游

| 数据集 | training seeds | 固定SID producer／v0 | 预期Testing用户数 | 状态 |
|---|---|---|---:|---|
| Beauty | 42／200／2026 | dq77e3wo | 22363 | 42 Done，其余Todo |
| Sports | 42／200／2026 | jcyr5l3p | 35598 | 三格Todo |
| Toys | 42／200／2026 | 3dycz43g | 19412 | 三格Todo |

同一数据集的三个推荐训练seed共用同一冻结SID，不重训embedding／quantizer。固定URI为 `wandb://baymaxam/GRID/<producer>?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt`。来源核对[BMX-115](https://linear.app/baymax104/issue/BMX-115)、TIGER34–42及 `docs/evidence/copmrec-hybrid-migration-20261018/source-matrix.json`。Sports／Toys的IntRR compact catalog SHA在实际启动前计算核准，当前不填造值。

## 4. 固定训练、选点与Testing协议

通用配置按用户选择与TIGER对齐：固定TFRecord划分与RKMeans SID；180 SID slots／最多44件历史商品，TIGER连续子序列增强最多32条。scratch、DDP2、FP32、train batch128/卡（global256）、validation batch64/卡，workers32/16；Adam lr=0.0005、weight_decay=0.000001，无scheduler、accumulate1、50,000 optimizer steps，无early stopping，每100步验证、log50，关闭训练后自动Testing。
IntRR内部参数固定 `configs/model/intrr.yaml`：UID512→模型256，共享RAN hidden512、STE、4层causal T5、6 heads／d_kv64、FF1024、dropout0.15、temperature1、alignment0.1。作者来源 commit `806e0f1969ed61a0748902649b335c0ea066de00`；alignment0.1与作者公开YAML0.0的差异已记录，不改为作者320k训练预算。
每格自身最高 `val/ndcg@10` 选唯一own-best，若并列取首次；固定checkpoint URI／SHA256后单卡Testing，batch32、workers8、beam10，全目录且无历史过滤、cold额外并入或目录重排。

这是以TIGER通用配置评测IntRR的基线，不能称为逐项复现原论文全部训练设置。其他基线保留各自原生SID、上游预算、hybrid或beam策略，不声称全方法全部配置相同。

## 5. 执行单元与预算

Beauty42已消费1训练×50k＋1Testing。待执行八格各1训练×50k＋1Testing：Beauty200／2026、Sports42／200／2026、Toys42／200／2026，计划新增 **8训练／400k更新／8Testing**；全部完成后IntRR总计9训练／450k／9Testing。该预算独立于BARS，不重置其既有700k或Untied剩8格400k计划；不含调参、额外seed、效率扫描、DECOR复现或上游重跑。
每格为独立可验收单元，不能合并成一次实验；当前新增实际训练／Testing／forward均0。失败或指标方向不自动触发重试或扩预算。

## 6. 执行方式

用户明确启动后，从node1仓库根目录经 `intrr_train.sh`／`intrr_inference.sh` 和统一 `src.main` 执行。Mutagen resume／flush／status确认三个session Watching且无conflict，核准来源、固定输入和空闲GPU／端口，再以独立tmux运行。实际run ID、输出目录、物理GPU、端口和checkpoint仅在执行后填写；本计划不预占资源。
训练50k结束并冻结本格own-best后才执行本格Testing；各格之间无必须串行依赖。不得根据Testing重选checkpoint。

## 7. Done门禁与汇总

1. 训练finished／exit0，达到50k更新；核对完整500次验证、首次最高val/NDCG@10及checkpoint step／SHA256／Artifact。
2. Testing finished／exit0，严格checkpoint contract与训练一致；核准固定SID、源码快照、数据划分及逐文件hash。
3. 输出keyed bundle `[N,10,4]`，用户集合完整唯一，SID合法、每行无重复；按原始TFRecord的user_id和末项target独立复算R@5、N@5、R@10、N@10，与W&B核准（容差1e-12）。
4. 保留SID、checkpoint、推荐输出lineage、resolved config、notes和实际run／输出身份。协议有效即可按实测结果Done，不把取胜作为验收条件。

九格全部有效后，按数据集保留全部逐seed四指标，再计算三seedmean±sample std（ddof=1），指标单位为比例。主指标NDCG@10，同时完整报告其余三项。与相同dataset／seed的当前BARS Untied、Shared对照和既有外部基线比较；Untied未完成格保留空缺，不以Shared替代或混算，不因IntRR完成而要求重跑有效旧baseline。

## 8. 证据解释与交付

实测较高、较低或混合均按完整矩阵如实报告，并据此调整相应质量表述；不预设IntRR应胜或应负。单seed或固定checkpoint用户区间不能代表训练seed稳定性，完整方法对比不单独证明共享、残差等组件的因果作用。
交付为九格身份与审计清单、三数据集三seed汇总、匹配比较来源和复现协议。保持BARS Untied当前主方法／Shared对照角色及已有Done事实。

## 9. Linear任务索引

父项：[BMX-195](https://linear.app/baymax104/issue/BMX-195)，状态Todo；归属M4“4. 多基线比较”。九格中Beauty42为Done，其余八格Todo。

| 数据集 | seed42 | seed200 | seed2026 |
|---|---|---|---|
| Beauty | [BMX-196](https://linear.app/baymax104/issue/BMX-196) Done | [BMX-197](https://linear.app/baymax104/issue/BMX-197) Todo | [BMX-198](https://linear.app/baymax104/issue/BMX-198) Todo |
| Sports | [BMX-199](https://linear.app/baymax104/issue/BMX-199) Todo | [BMX-200](https://linear.app/baymax104/issue/BMX-200) Todo | [BMX-201](https://linear.app/baymax104/issue/BMX-201) Todo |
| Toys | [BMX-202](https://linear.app/baymax104/issue/BMX-202) Todo | [BMX-203](https://linear.app/baymax104/issue/BMX-203) Todo | [BMX-204](https://linear.app/baymax104/issue/BMX-204) Todo |

Beauty42复用已完成训练与Testing，其余8格为待执行计划；该索引不构成启动指令。
