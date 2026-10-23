# BARS 当前方法 M3：机制与匹配消融结果

日期：2026-10-23。协议：`bars-fixed-half-hybrid-m3-20261023-v1`，范围Beauty／training seed42。**三个匹配消融、C固定模型机制分析及正式配对贡献均完成并通过独立验收，当前M3阶段收口。** Full相对Shared和双侧零残差的NDCG@10分别提高17.38%和26.26%；移除当前唯一Catalog CE后，NDCG@10相对Full下降77.03%。三组组件比较的四指标用户区间均为正；固定当前Full时，生成引导和同池目录排序也获得支持。结论限定为当前Beauty42训练来源，追加实验与预算均为0。

当前Full固定alpha0.5、SID/Catalog/mixture权重1/1/0，hybrid Validation及推荐共用beam20＋全部cold、目录logits稳定Top10、无历史排除。三个匹配新臂和C固定模型干预分别回答[原计划](bars-current-method-m3-plan-20261023.md)的问题；旧learned-alpha、三损失、dense选点结果保持历史身份，不参与本表。

## 运行、训练与自身best来源

三个新臂均完成scratch50k、100次非空hybrid Validation、finished／exit0，按自身首次最高val/NDCG@10选点。checkpoint发布文件MD5/SHA、variant契约、optimizer、上游和323份来源文件通过[训练独立审计](evidence/bars-current-method-m3-test-20261023/training-audit.json)。Full只复用当前已验收来源，不重复训练或Testing。

| 条件 | loss SID/Catalog/mixture | Training | 首次own-best | 唯一正式Testing |
| --- | --- | --- | ---: | --- |
| Full，Untied | 1/1/0 | `httwyhka`，复用 | 46000 | `prt5r0v5`，复用 |
| Shared | 1/1/0 | `gu3l2s2s` | 47500 | `e0m3cdsi` |
| 双侧零残差 | 1/1/0 | `1k2ebqaw` | 43500 | `1ipsthvi` |
| Untied去直接Catalog CE | 1/0/0 | `7u93dubs` | 45500 | `srta7ooi` |

| 条件 | checkpoint SHA256 | prediction SHA256 |
| --- | --- | --- |
| Full | `f2ffd7939483c4e16fa9359a2a856865386d0823d6285321c53df1f1391ca4c9` | `7bd54d23e33b6b89b4d7de568f030172819293417fd5f74a4fc39a5ca1097065` |
| Shared | `5e1bb7806e5decdb074d7cdcb09ef9fea79b1e5759995d4d4628a4447b5b678a` | `a7a47e886f2698fea299ec652698ceab7ec60b9f560106a931e6d3bb9d139593` |
| 双侧零残差 | `a9d70ace53fefd41e9702eb282644a953b9ae949f18780acb8a59b2a5440a23b` | `6a7a630944600f03f2357d14ce18d7de62fb0a1c1ff2050f55178df2ee14311b` |
| 去直接Catalog CE | `553052d25ae875d65483385017b8dc784b426655f8360cdd9d6ee00ec94485f0` | `2e7ada688e486bdc935e702cd9893c16ab33598aaef52f6fca740e8e7f9d9cd6` |

完整不可变URI、Artifact版本／digest、source、lineage和逐来源审计分别见[Full](evidence/bars-current-method-m3-test-20261023/independent-untied.json)、[Shared](evidence/bars-current-method-m3-test-20261023/independent-shared.json)、[零残差](evidence/bars-current-method-m3-test-20261023/independent-no_residual.json)、[去CE](evidence/bars-current-method-m3-test-20261023/independent-no_joint_ce.json)。三臂的`last.ckpt`实际等于own-best步数；50k终点由完整验证序列、console及exit0共同核验，未将last用作终点或Testing来源。

## A／B：匹配组件四指标

全部四来源为同一22,363用户和真实标签，预测形状 `[22363,10,4]`，全量key、合法唯一Top10、checkpoint／上游／源码／输出文件字节均核验通过。审计使用两条独立rank计算路径复算四指标，与W&B最大误差 `5.90e-17`，审计新增模型forward为0。见[Testing总审计](evidence/bars-current-method-m3-test-20261023/independent-testing-audit.json)及[冻结验收来源](evidence/bars-current-method-m3-test-20261023/independent-accepted-sources.json)。

| 条件 | Recall@5 | NDCG@5 | Recall@10 | NDCG@10 |
| --- | ---: | ---: | ---: | ---: |
| Full | 0.05392836 | 0.03842789 | 0.07512409 | 0.04527919 |
| Shared | 0.04619237 | 0.03052779 | 0.07114430 | 0.03857355 |
| 双侧零残差 | 0.04261503 | 0.02761401 | 0.06819300 | 0.03586154 |
| 去直接Catalog CE | 0.01064258 | 0.00635836 | 0.02329741 | 0.01040216 |

| 主指标比较，Full减对照 | NDCG@10差值 | Full相对对照变化 | 95%用户配对区间 |
| --- | ---: | ---: | --- |
| Full−Shared | +0.00670565 | +17.38% | [0.00522777, 0.00817414] |
| Full−双侧零残差 | +0.00941765 | +26.26% | [0.00712597, 0.01160523] |
| Full−去直接Catalog CE | +0.03487703 | +335.29% | [0.03252653, 0.03714077] |

以上差值和百分比是已验收模型的点估计，Full相对增益的分母为各对照；去CE下降77.03%的分母为Full。去CE对应1/0/0移除当前唯一目录判别目标后的系统变化，不能沿用旧1/0/1的“mixture监督之上额外CE价值”解释。共享投影仍会由SID路径更新；Shared比较同时改变残差容量、共享约束和梯度耦合，不单独归因某条梯度路径。

正式零forward贡献分析 `6cpl285w` 于13:31:29在CPU提交，现已finished／exit0并独立验收，仅读取上述四份验收bundle与真实标签，不新增训练或推荐forward。4个来源、89,452行用户CSV、4个bundle、12项配对区间、24项命中类别、全部文件MD5/SHA及Artifact lineage核验通过。发布Artifact为 `baymaxam/GRID/bars_untied_beauty_seed42_contributions-analysis:v2`，digest `ee06a71c52403bf3bb20259d0754d2d3`；不能与历史版本混用。来源和提交见[plan](evidence/bars-current-method-m3-test-20261023/contributions-plan.json)、[submit](evidence/bars-current-method-m3-test-20261023/contributions-submit.json)，独立完成及统计见[completion](evidence/bars-current-method-m3-test-20261023/independent-contributions-completion.json)、[audit](evidence/bars-current-method-m3-test-20261023/independent-contributions-audit.json)。

所有比较按完整真实用户key配对，PCG64／seed42／2000次bootstrap，四指标共用每次抽样，区间为95% pointwise percentile。下表完整列出12项差值及分解；gain、loss和共同命中排名变化以全体用户均值计，在完整精度下严格加和为总差。三个对照的四指标区间均高于零。

| Full减对照 | 指标 | 差值 | 95%用户CI | gain | loss | 共同命中排名 |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| Shared | recall@5 | +0.00773599249 | [0.00545543979, 0.01001766310] | +0.01918347270 | -0.01144748021 | +0.00000000000 |
| Shared | ndcg@5 | +0.00790009844 | [0.00637915640, 0.00945642811] | +0.01164091387 | -0.00627270777 | +0.00253189233 |
| Shared | recall@10 | +0.00397978804 | [0.00138621831, 0.00648392434] | +0.02061440773 | -0.01663461968 | +0.00000000000 |
| Shared | ndcg@10 | +0.00670564599 | [0.00522777408, 0.00817413974] | +0.00986591538 | -0.00671225989 | +0.00355199051 |
| 双侧零残差 | recall@5 | +0.01131333005 | [0.00827147520, 0.01431046818] | +0.03438715736 | -0.02307382730 | +0.00000000000 |
| 双侧零残差 | ndcg@5 | +0.01081387664 | [0.00843546588, 0.01308356009] | +0.02403953217 | -0.01414250763 | +0.00091685209 |
| 双侧零残差 | recall@10 | +0.00693109154 | [0.00326432053, 0.01024012878] | +0.03881411260 | -0.03188302106 | +0.00000000000 |
| 双侧零残差 | ndcg@10 | +0.00941765153 | [0.00712596503, 0.01160523189] | +0.02297190348 | -0.01524032038 | +0.00168606844 |
| 去Catalog CE | recall@5 | +0.04328578455 | [0.04024392971, 0.04632763940] | +0.04999329249 | -0.00670750794 | +0.00000000000 |
| 去Catalog CE | ndcg@5 | +0.03206953046 | [0.02975866562, 0.03439260270] | +0.03575121229 | -0.00381978369 | +0.00013810186 |
| 去Catalog CE | recall@10 | +0.05182667799 | [0.04833877387, 0.05531570004] | +0.06318472477 | -0.01135804677 | +0.00000000000 |
| 去Catalog CE | ndcg@10 | +0.03487703180 | [0.03252653312, 0.03714077474] | +0.03779331139 | -0.00507435197 | +0.00215807238 |

## C：当前Full的生成与排序用途

`gkwknl0l`于02:44:57 finished／exit0；[独立机制审计](evidence/bars-current-method-m3-test-20261023/mechanism-audit.json)全部通过。仅使用Full own-best46000，固定alpha0.5、不更新参数。production＋catalog臂对 `prt5r0v5` 全部22,363用户每个Top10位置完全一致；五份合法唯一列表、源码、四项上游Artifact lineage与发布文件实际字节齐全。

下表指标为按冻结预测rank独立复算的float64，完整精度见审计JSON。

| 生成 | 最终排序 | Recall@5 | NDCG@5 | Recall@10 | NDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| production，固定0.5 | catalog | 0.05392836 | 0.03842789 | 0.07512409 | 0.04527919 |
| production，固定0.5 | 合法decoder完整SID logP | 0.02839512 | 0.01760032 | 0.05044046 | 0.02468089 |
| alpha0 | catalog | 0.03765148 | 0.02611773 | 0.05450968 | 0.03156069 |
| alpha0 | 合法decoder完整SID logP | 0.02718777 | 0.01699121 | 0.04641595 | 0.02318063 |
| dense辅助参考 | catalog | 0.05388365 | 0.03839867 | 0.07512409 | 0.04525960 |

每种生成条件实际搜索一次beam20，并入全部33个cold商品后，在该条件的同一候选池上比较两种排序。production与alpha0的候选覆盖分别2,442／1,749用户，纯beam覆盖分别2,304／1,611用户；两种条件的all-cold各另覆盖138用户。production相对alpha0净增加693名候选覆盖用户。

以下配对差与CI沿用实际发布的float32逐用户指标，独立逐项重放PCG64／seed42／2000次用户bootstrap；共24项指标区间核验通过。不能将本表float32统计与上表float64精确值混为同一数值口径。

| NDCG@10比较 | 差值 | 95%用户配对CI |
| --- | ---: | --- |
| production−alpha0，固定catalog排序 | +0.01371851 | [0.01190906, 0.01552176] |
| production−alpha0，固定decoder排序 | +0.00150027 | [0.00093817, 0.00208979] |
| catalog−decoder，固定production池 | +0.02059830 | [0.01853080, 0.02273989] |
| catalog−decoder，固定alpha0池 | +0.00838006 | [0.00700500, 0.00982482] |
| production/catalog−alpha0/decoder | +0.02209856 | [0.01995930, 0.02431495] |
| 生成×排序交互 | +0.01221824 | [0.01023956, 0.01414752] |

C支持固定当前模型时生成引导和同池catalog排序的质量用途及正交互。固定catalog的生成差由最终左独有命中 `+0.02282529`、右独有命中 `−0.00581339`、共同命中排名 `−0.00329340` 加和；不能将左独有最终命中直接称为新增候选贡献。完整40项类别分解、24项区间及贡献守恒通过，详见[C结果与边界](evidence/bars-current-method-m3-test-20261023/mechanism-results.md)。

这些区间描述固定训练来源下的用户抽样，不估计训练seed变动。C不建立alpha0.5全局最优性；dense辅助与production的NDCG@10仅差约`1.96e-5`，不据此声称hybrid显著优于dense或有效率优势。中间完整beam／候选ID／逐候选score未持久化，coverage和同池语义由记录一致性、归档实现及已有测试核验，未新增forward重建。

## 预定判断、累计成本与阶段收口

本阶段预定3训练／150k、3次各自身own-best Testing均已完成且独立验收，Full复用不再次计费；C一次固定模型分析和`6cpl285w`一次零forward贡献分析也完成独立验收。原750k历史M3、M2九格和其他阶段各自账本保持；本轮新增训练0、训练重试0、调参0、上游0，剩余执行0、追加实验及预算0。

按原计划的正向／负向／uncertain规则，本次三组均通过有效性门禁并提供正向主指标区间：A保留商品行为适配的净质量贡献，并支持当前Untied相对匹配Shared的表示选择；B保留当前唯一目录判别目标在两损失系统中的作用；C保留固定当前模型下生成引导、同池目录排序及其正交互。其他四指标和损失贡献全部保留，不据净收益声称所有用户改善。

当前M3据此收口，不新增seed、数据集、权重／alpha扫描或机制预算。用户区间只描述固定Beauty42训练来源下的抽样差异，不估计训练seed稳健性；Shared差异不能唯一识别容量、共享约束或梯度冲突。C、A/B重训对照及表示比较分别解释，不将差值相加为总收益分解或因果中介。论文与PDF本轮不修改，当前结果不自动授权后续执行。

北京时间13:37:51的[Linear最终实时回读](evidence/bars-current-method-m3-test-20261023/linear-final-readback.json)确认当前五项205／194／206／207／208全部Done、M3里程碑100%，子项父关系保持；M2父项及九格继续全部Done。
