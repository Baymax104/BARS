# BARS Untied Beauty42 机制结果与论文主线

日期：2026-10-19。阶段协议 `bars-untied-mechanism-beauty42-20261019-v1`，父项 [BMX-205](https://linear.app/baymax104/issue/BMX-205)。A／B／C 已完成，正式运行、不可变来源与独立逐用户验收均通过。

**当前 Beauty／seed42 已形成相互衔接的证据链：商品级行为适配提高推荐质量，直接目录 CE 在 SID CE＋mixture NLL 之外提供额外增益；固定模型时，目录相关性改善候选覆盖和同池排序，二者呈正交互。M3 机制阶段据此收口，追加机制实验与训练预算均为0。**

## 论文主线

保留内容 SID 的组织结构，分别学习历史侧与目录侧商品行为表示，通过直接商品监督形成目录相关性，再将同一相关性用于合法前缀生成与最终排序。完整方法比较承担效果证据，角色表示对照与重训移除解释设计选择，固定 checkpoint 干预定位推理链路。贡献组织围绕这一完整方法及其用途展开。

## 运行与有效性

| 组别 | 实际来源 | 完成事实 |
| --- | --- | --- |
| A 商品适配贡献 | [84a07f71](https://wandb.ai/baymaxam/GRID/runs/84a07f71)，复用 Untied／Shared／原 no_residual | 22,363用户，0模型forward，预测／标签／bootstrap／贡献守恒独立验收通过 |
| B 去直接目录CE | train [ec98cca4](https://wandb.ai/baymaxam/GRID/runs/ec98cca4)；Test [0474e89a](https://wandb.ai/baymaxam/GRID/runs/0474e89a)；贡献 [3e62b44e](https://wandb.ai/baymaxam/GRID/runs/3e62b44e) | 50k／100次Validation／exit0；首次自身最高step49,000；一次hybrid Test及配对分析通过 |
| C 生成×排序2×2 | [1241f8aa](https://wandb.ai/baymaxam/GRID/runs/1241f8aa)，固定Full `g953gzcq` step39,500 | 0训练；四臂及dense参考；production逐用户Top10精确复现；独立产物验收通过 |

Beauty三个split共525个分片、SID／内容Artifact、12,101商品及seen-mask保持冻结来源。B保留双表和原配方，仅将直接joint catalog CE权重设0；mixture NLL仍对目录路径提供监督。正式部署为beam20＋all cold、catalog logits稳定Top10、无历史排除。

B自身best不可变URI为 `wandb://baymaxam/GRID/ec98cca4?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=049000.ckpt`，SHA256为 `075749c79484c0eb002a6801e11dbd25bc7dfddaf0040d717a34d3b7f7009885`。完整100点Validation、训练来源归档、Artifact与checkpoint字节回读通过，未使用last或Full替代新臂自身best。

## A：行为适配及角色独立表示

| 比较 | Full NDCG@10 | 对照 NDCG@10 | Full−对照 | 相对对照提升 | 95%用户配对CI |
| --- | ---: | ---: | ---: | ---: | --- |
| Untied−共同零残差 | 0.04546932 | 0.03598946 | +0.00947986 | 26.34% | [0.00716641, 0.01154454] |
| Untied−Shared | 0.04546932 | 0.03967024 | +0.00579909 | 14.62% | [0.00432065, 0.00734550] |

两组四指标区间均高于零。相对共同零残差的NDCG@10贡献为新增命中 `+0.02242031090`、丢失命中 `-0.01608543736`、共同命中排名 `+0.00314498729`，三项守恒。当前证据支持商品行为适配与角色独立设计选择；Untied／Shared同时改变容量与共享约束，不把收益单独归因为梯度冲突。

## B：直接商品监督的额外作用

| 指标 | Full | Untied去直接目录CE | Full−移除臂 | 95%用户配对CI |
| --- | ---: | ---: | ---: | --- |
| Recall@5 | 0.05433081 | 0.04990386 | +0.00442696 | [0.00254885, 0.00634977] |
| NDCG@5 | 0.03868193 | 0.03576655 | +0.00291538 | [0.00173768, 0.00414015] |
| Recall@10 | 0.07539239 | 0.07083128 | +0.00456111 | [0.00223584, 0.00670751] |
| NDCG@10 | 0.04546932 | 0.04252142 | +0.00294790 | [0.00183797, 0.00408401] |

主NDCG@10相对移除臂提高 **6.93%**，四指标区间均高于零。NDCG@10差值的新增命中贡献 `+0.00676821401`、丢失命中 `-0.00474177940`、共同命中排名 `+0.00092146872` 精确加和。Top10新增命中374人、丢失272人、共同命中1,312人、共同未命中20,405人。

这一重训对照支持直接目录CE在当前Untied条件下的额外价值。由于SID CE与mixture NLL保留，准确表述是“移除直接目录CE”，而非“移除全部目录监督”。

## C：目录相关性的生成与排序用途

固定Full参数与gate；每个生成条件真实搜索一次beam20，再并入全部cold。两个ranker处理同一生成条件的同一个候选池；decoder对全部候选含cold计算完整合法SID路径log概率。真实标签只参与测量。

| 生成 | 最终排序 | Recall@5 | NDCG@5 | Recall@10 | NDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| learned mixture | catalog | 0.05433081 | 0.03868193 | 0.07539239 | 0.04546933 |
| learned mixture | decoder | 0.03461074 | 0.02091728 | 0.06112776 | 0.02944390 |
| alpha0 decoder | catalog | 0.03845638 | 0.02662937 | 0.05504628 | 0.03197869 |
| alpha0 decoder | decoder | 0.02803738 | 0.01766311 | 0.04771274 | 0.02395234 |
| 全目录辅助参考 | catalog | 0.05428610 | 0.03866463 | 0.07530296 | 0.04544050 |

| 预定对比 | NDCG@10差值 | 95%用户配对CI |
| --- | ---: | --- |
| 固定 catalog 排序：learned−alpha0 | +0.01349063 | [0.01163027, 0.01528816] |
| 固定 decoder 排序：learned−alpha0 | +0.00549156 | [0.00431008, 0.00660851] |
| 同 learned 池：catalog−decoder | +0.01602543 | [0.01421758, 0.01797514] |
| 同 alpha0 池：catalog−decoder | +0.00802635 | [0.00660980, 0.00944618] |
| 完整组合−alpha0/decoder | +0.02151698 | [0.01933444, 0.02375780] |
| 生成×排序交互 | +0.00799908 | [0.00600544, 0.01002460] |

目录相关性在两种固定ranker下都带来生成收益；catalog在两个生成池上均有排序收益，四指标的预定比较均为正向。正交互表明两阶段的用途互补；它是本次固定Full checkpoint及两个备选条件之间的经验交互。

纯beam目标覆盖从 **7.2844%（1,629人）** 提高到 **10.4861%（2,345人）**，增加716人、3.2017个百分点。并入cold后覆盖分别为7.9014%和11.1032%，两条件额外cold覆盖均为138人；因此覆盖差并非由额外cold数量不同造成。这些覆盖数为点估计，不填造未输出的区间。

生成干预在catalog排序下的NDCG10变化由独有命中 `+0.02293708`、丢失命中 `−0.00662939`、共同命中排名 `−0.00281706` 组成，净收益主要表现为覆盖与命中改善。同learned候选池改用catalog排序时，共同命中排名贡献为 `+0.00530779`，与排序职责一致。

## 证据层次与阶段决定

此次保留“商品行为适配—直接商品监督—相关性贯通生成与排序”的主线，M3新增实验数0、追加训练预算0。A/B来自各自训练来源的比较，C为固定模型干预，三组差额不相加为总收益分解或因果中介。learned alpha约0.993415；当前alpha0对照证明目录相关性在搜索中的用途，不单独证明learned gate必要，也不比较纯mass端点。

dense辅助NDCG@10为0.04544050，production为0.04546933，差约0.00002883。它保留为辅助参考，本阶段不据此提出hybrid质量明显优于dense、统计等价或效率优势。C按原诊断float32逐用户值汇总，NDCG10与正式Full double复算相差约6e-10，production Top10本身逐用户精确一致。

统计采用预定PCG64 seed42、2000次共享用户抽样、95% pointwise区间；它描述固定训练来源下的用户抽样不确定性，不估计训练seed稳定性。当前结果范围为Beauty／seed42，多数据集多seed承担独立的外部有效性证据。

本阶段实际新增1×50k＋1次正式Test，A和C各一次分析，另一次新Test预测贡献分析，未追加训练或重复Test。M3完成账本为此前700k＋本次50k＝750k；另行授权M2矩阵使用独立账本与运行记录，本轮不启动、暂停或干预该任务。IntRR扩展保持其自身计划状态。

## 可追溯证据

[结果JSON](evidence/bars-untied-mechanism-launch-20261019/mechanism-results.json)、[完成运行回读](evidence/bars-untied-mechanism-launch-20261019/completion-collection.json)、[A独立审计](evidence/bars-untied-mechanism-launch-20261019/A-result-audit.json)、[B独立审计](evidence/bars-untied-mechanism-launch-20261019/B-test-result-audit.json)、[C独立审计](evidence/bars-untied-mechanism-launch-20261019/C-result-audit.json)、[启动记录](evidence/bars-untied-mechanism-launch-20261019/README.md)、[原阶段问题与判断规则](bars-untied-mechanism-plan-20261019.md)。
