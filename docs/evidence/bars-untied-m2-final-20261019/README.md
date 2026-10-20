# BARS Untied M2：最后一格Testing与九格结项回执

用户明确要求将已完成训练进行下一步并更新Linear。本轮为BMX-193 Toys／seed2026执行唯一一次自身own-best hybrid Testing，训练和预测独立验收均通过；M2完整结果从8/9补齐为 **9/9**。父项[BMX-185](https://linear.app/baymax104/issue/BMX-185)及[BMX-193](https://linear.app/baymax104/issue/BMX-193)已Done，其余七个新增格保持Done；Beauty42按原身份复用。

## 最后一格结果

训练[zurt85mz](https://wandb.ai/baymaxam/GRID/runs/zurt85mz)于2026-10-19 23:34:23（北京时间）完成50,000 updates、100次dense Validation，exit0。首次最高val/ndcg@10对应own-best **41000**；Testing [kq3j4vm5](https://wandb.ai/baymaxam/GRID/runs/kq3j4vm5)于2026-10-19 23:53:02至2026-10-19 23:54:46在GPU3单卡运行并exit0。

| 指标 | Untied | Shared | Untied相对Shared | Shared−Untied 95%用户CI |
| --- | ---: | ---: | ---: | --- |
| recall@5 | 0.058984133526 | 0.055996290954 | +5.3358% | [-0.005202967237, -0.000616886462] |
| ndcg@5 | 0.043653645369 | 0.039523053898 | +10.4511% | [-0.005701391664, -0.002563933188] |
| recall@10 | 0.077941479497 | 0.076550587266 | +1.8170% | [-0.004069647641, 0.001339377705] |
| ndcg@10 | 0.049767194794 | 0.046093609496 | +7.9698% | [-0.005175289159, -0.002181300250] |

主指标结果登记为`untied_better`。配对bootstrap使用PCG64、seed42、2000次、95% pointwise区间，方向为Shared−Untied，另逐次独立重放；用户抽样区间与下方训练seed样本标准差分别报告。

## 三数据集三seed汇总

以下为seed42／200／2026实际结果的原比例均值±样本标准差（ddof=1）。Beauty与Sports复用已验收来源并按逐格值重算；Toys42／200的两条件完整预测在本轮再次只读核验。

| 数据集 | 指标 | Untied mean ± sample std | Shared mean ± sample std |
| --- | --- | ---: | ---: |
| beauty | recall@5 | 0.053436479900 ± 0.000775806089 | 0.047951228965 ± 0.000211322972 |
| beauty | ndcg@5 | 0.038229133506 ± 0.000418791357 | 0.031541788485 ± 0.000441205838 |
| beauty | recall@10 | 0.074751449567 ± 0.000566215621 | 0.072217502124 ± 0.000527202349 |
| beauty | ndcg@10 | 0.045093347010 ± 0.000372867605 | 0.039350623716 ± 0.000539878540 |
| sports | recall@5 | 0.027454725921 ± 0.000732715327 | 0.027117628331 ± 0.001017645418 |
| sports | ndcg@5 | 0.018587303921 ± 0.000285385409 | 0.017753087823 ± 0.000505299589 |
| sports | recall@10 | 0.041256999457 ± 0.000203218668 | 0.041612824691 ± 0.000818678690 |
| sports | ndcg@10 | 0.023037430746 ± 0.000127501187 | 0.022419377806 ± 0.000471367467 |
| toys | recall@5 | 0.059207363143 ± 0.000301847583 | 0.054433683632 ± 0.001477248864 |
| toys | ndcg@5 | 0.043756182812 ± 0.000092030736 | 0.038672209329 ± 0.000867521515 |
| toys | recall@10 | 0.077958651006 ± 0.000180913074 | 0.076104128031 ± 0.000464583737 |
| toys | ndcg@10 | 0.049795891334 ± 0.000177514811 | 0.045653802305 ± 0.000533583249 |

## 验收与来源

完整19,412用户keys及真实标签SHA与冻结输入一致；输出形状[19412,10,4]，全部SID合法且逐用户Top10无重复。W&B summary、既有helper与独立tuple-rank复算一致，最大summary差3.47e-17。不可变v0输出、checkpoint URI／SHA与Artifact lineage通过。

- checkpoint：`wandb://baymaxam/GRID/zurt85mz?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=041000.ckpt`
- checkpoint SHA256：`4a504fefd2ba7f1ba2970a8aa024878827a60278ae15c5f5073030759e88d779`
- prediction：`wandb://baymaxam/GRID/kq3j4vm5?role=recommendation_output&alias=v0&file=merged_predictions_tensor.pt`
- prediction SHA256：`e4020543ac4273f28166f60900de0fbf6a8b4a98f83e4ca87b3293f0c7a64964`

训练审计见[training-audit.json](training-audit.json)，预测、逐格来源、全部四指标和区间见[testing-audit.json](testing-audit.json)与[zero-forward-results.json](zero-forward-results.json)。全矩阵9个dataset×seed组合、9个唯一Test及原训练身份已由[最终核验](final-verification.json)验证。

## 执行与预算

独立tmux：`bmx-193-untied-test-20261019_235237`；输出：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-193_test_20261019_235237`；批次：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_test_final_20261019_235237`。实际命令、冻结输入和启动守卫见[next-testing.json](next-testing.json)及[bmx-193-test.sh](bmx-193-test.sh)，[预检](prepare.json)、[提交](submit.json)、[结束状态](status.json)记录实际时点。

统一根脚本经src.main执行；FP32、mixture beam20+全部cold、joint catalog logits和stable catalog-row Top10、checkpoint learned alpha、无历史排除保持原协议。152个Testing分片path／size／SHA与冻结输入一致；shell语法与Hydra compose通过；Mutagen flush成功且三session Watching for changes，320文件source SHA保持原值。GPU3启动时低利用率且至少8GB显存余量；未停止其他进程。

M2新增8格训练共400k／授权400k全部完成，8次计划Testing全部完成；加Beauty42复用结果，全矩阵9/9验收通过。本轮新增训练0、训练重试0、Testing1；审计新增模型forward0。原M3、Shared与IntRR账本保持独立，未追加seed、调参、训练或推理预算。

## 状态记录

[Linear写回](linear-update.json)和[回读](linear-readback.json)记录父子项Done；[研究记录验证](research-records-verification.json)记录research-state.yaml及两份计划同步。现有论文与PDF仍绑定原构建，本次未更新稿件。

[上一轮8/9回执](../bars-untied-m2-test-next-20261019/README.md)与[初次启动](../bars-untied-m2-launch-20261019/README.md)保留原历史时点。
