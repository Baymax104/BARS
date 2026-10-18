# CoPMRec v2 hybrid 主版本迁移完成证据

2026-10-18，`copmrec-hybrid-migration-20261018-v1` 已完成：node1 tmux运行13次正式单卡Testing与1次零模型forward hits，全部finished/exit0且独立审计passed。新增训练、optimizer updates、独立Validation、残差/真实前缀重跑均为0；累计训练650k与历史成本保留。未创建持续监控。

## 当前主版本与部署

主方法为CoPMRec v2 learned-alpha Full hybrid。checkpoint自身实际mixture概率生成beam20，与全部cold商品合并去重，再在候选内按joint catalog logits稳定catalog-row Top10，无历史排除。训练、dense Validation和各自own-best不改；no_mixture搜索精确alpha0.5，fixed_alpha_one精确1。

入口默认hybrid；旧dense有效辅助通过显式`--deployment dense`复现，旧hits显式`hits_deployment_mode=dense`。BMX-149 LIGER dense仅可选辅助；162残差2×2 dense辅助、163真实前缀继续有效，均不重跑。当前仍计算全目录logits/prefix mass，本批不建立效率收益主张。

## 正式主结果

三seed=42/200/2026，sample std使用ddof=1。

| Dataset | CoPMRec hybrid NDCG@10 mean ± std | LIGER hybrid NDCG@10 mean ± std | 相对变化 |
| --- | ---: | ---: | ---: |
| beauty | 0.03935062 ± 0.00053988 | 0.02992889 ± 0.00024044 | +31.4804% |
| sports | 0.02241938 ± 0.00047137 | 0.01574162 ± 0.00040768 | +42.4210% |
| toys | 0.04565380 ± 0.00053358 | 0.02629864 ± 0.00054926 | +73.5976% |

全部四指标、逐格来源及Beauty消融/alpha1用户区间见[正式结果](../../../../research/docs/copmrec-hybrid-results-20261018.md)和[aggregates.json](aggregates.json)。三移除臂的Beauty42 NDCG@10用户区间低于Full；alpha1 NDCG@10及四臂Recall@10区间跨零。no_mixture改变训练与候选，按系统消融解释；用户区间不代表训练seed不确定性。

## 来源与独立核验

[source-matrix.json](source-matrix.json)冻结13个原自身checkpoint与baseline版本；[execution-plan.json](execution-plan.json)记录真实14run、实际GPU/tmux、完整命令位置、URI/SHA、指标与完成状态。正式源码SHA256 `154f2ae8e76c30b49209d16cbfbea338713367ec742ee623f452b585809ab3e9`，每run298文件与[本地origin](local-origin-verification.json)逐项hash/size一致，不依赖远端Git判断版本。

- [audit.json](audit.json)：13/13 prediction独立passed，own-best/SHA/variant/seed、源归档/输入lineage、真实labels/keys、实际hybrid metadata、合法唯一Top10通过，最大四指标summary复算误差6.245e-17。
- [final-audit-receipt.json](final-audit-receipt.json)：完整审计及aggregates、paired、slices的文件SHA。
- [hits-audit.json](hits-audit.json)：run `ppjhagjq`，22363用户/89452记录，4正式bundle逐元素一致；分解守恒在浮点容差内通过，确定性case/slice全部核验，切片均值和配对CI复算误差0。分析和审计均0次模型forward。
- 分析Artifact `copmrec_v2_beauty_seed42_hybrid_hits_full_diagnosis-analysis:v0`，digest `12571441d7c40ceb8ca0e21bb5c08937`，登记于hits-audit.json。[hits-audit-receipt.json](hits-audit-receipt.json)确认原prediction与gate审计字节不变；其中hits-audit SHA是审计文件SHA，与Artifact digest分开。
- [final-execution-receipt.json](final-execution-receipt.json)：14真实run及两端执行计划终态。
- [gate-result.json](gate-result.json)、[audit-gate.json](audit-gate.json)：首两格正式gate独立保留；临时聊天结果未直接升级为正式Artifact。

## 实现验证与计划迁移

[validation.json](validation.json)：177项聚焦单测通过，覆盖模型/严格旧checkpoint恢复、Hydra compose、脚本语法及quoting/空值/错误/override透传、实际metadata与hybrid输入门禁。Ruff、OpenSpec strict、git diff --check通过。Mutagen flush后三session均Watching for changes、无conflict。

- [linear-legacy-update-readback.json](linear-legacy-update-readback.json)：30项既有协议/结果/基线引用角色更新，原执行代码和Done状态保留。
- [linear-m5-update.json](linear-m5-update.json)：41项Todo八章论文计划逐条更新与读回；撤去149 dense正文硬门槛及过期LETTER占位，原证据来源与元信息保持。
- [linear-new-completion.json](linear-new-completion.json)：168/169/170–183共16项正式结果登记及逐项读回；实现167单独Done。
- [linear-final-project-docs-readback.json](linear-final-project-docs-readback.json)：项目、5个milestone、4份文档及全量121任务核对，原104项状态不变，17个新增迁移任务均Done；M5写作任务仍Todo。
- [research-final-verification.json](research-final-verification.json)：研究YAML、schema、14来源/状态/指标/CI/预算逐项一致，4个旧state块字节SHA保持。
- [迁移计划](../../../../research/docs/copmrec-hybrid-migration-plan-20261018.md)与[Run Registry](../../../../research/docs/copmrec-v2-run-registry-20261009.md)：当前主版与dense辅助分列。

13+1预算已结案，没有扩展beam/alpha扫描、seed、数据集或新增训练。
