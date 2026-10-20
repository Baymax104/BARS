# LETTER 基线主表（BMX-130，2026-10-10）

BMX-130完成：准备任务BMX-58与九个正式单元BMX-60～68均Done；Beauty/Sports/Toys各seed42/200/2026的正式训练与Testing完成。本文汇总已经独立核验的最终Testing，当前W&B状态、exit、summary和固定产物在本轮再次回读核对。

## 主表

| Dataset | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|
| Beauty | 0.041780322 ± 0.003129319 | 0.064436793 ± 0.004992077 | 0.027537013 ± 0.002098407 | 0.034818369 ± 0.002704864 |
| Sports | 0.021246512 ± 0.000777648 | 0.033073019 ± 0.001379155 | 0.013651766 ± 0.000315475 | 0.017457534 ± 0.000534168 |
| Toys | 0.034136960 ± 0.000747109 | 0.054107425 ± 0.000579014 | 0.022269287 ± 0.000467789 | 0.028696102 ± 0.000269282 |

每个数据集对三个seed等权计算均值±样本标准差（ddof=1），指标为原始比例，不乘100，不跨数据集合并用户。主表直接使用九个指定Testing run的test/recall@5、test/recall@10、test/ndcg@5、test/ndcg@10 summary，与原始目标和输出bundle独立复算记录逐项差≤1e-12。CSV见 [可复用主表数据](letter-main-table-20261010.csv)，mean/std列分开保留。

## 九个正式实验单元

| Issue | Dataset | seed | Testing run | 用户数 | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
|---|---|---:|---|---:|---:|---:|---:|---:|
| BMX-60 | Beauty | 42 | [wvpeeti8](https://wandb.ai/baymaxam/GRID/runs/wvpeeti8) | 22363 | 0.039305997 | 0.060009838 | 0.025693202 | 0.032364410 |
| BMX-61 | Beauty | 200 | [da4bbei4](https://wandb.ai/baymaxam/GRID/runs/da4bbei4) | 22363 | 0.040736932 | 0.063453025 | 0.027097455 | 0.034372072 |
| BMX-62 | Beauty | 2026 | [jhdcssd1](https://wandb.ai/baymaxam/GRID/runs/jhdcssd1) | 22363 | 0.045298037 | 0.069847516 | 0.029820381 | 0.037718625 |
| BMX-63 | Sports | 42 | [3iia84nm](https://wandb.ai/baymaxam/GRID/runs/3iia84nm) | 35598 | 0.021967526 | 0.034608686 | 0.014012800 | 0.018074308 |
| BMX-64 | Sports | 200 | [efy52sdx](https://wandb.ai/baymaxam/GRID/runs/efy52sdx) | 35598 | 0.020422496 | 0.031939997 | 0.013429234 | 0.017143913 |
| BMX-65 | Sports | 2026 | [74u0edre](https://wandb.ai/baymaxam/GRID/runs/74u0edre) | 35598 | 0.021349514 | 0.032670375 | 0.013513263 | 0.017154379 |
| BMX-66 | Toys | 42 | [jeslrexe](https://wandb.ai/baymaxam/GRID/runs/jeslrexe) | 19412 | 0.034154131 | 0.053472079 | 0.022769337 | 0.028977509 |
| BMX-67 | Toys | 200 | [yn904aco](https://wandb.ai/baymaxam/GRID/runs/yn904aco) | 19412 | 0.033381414 | 0.054605399 | 0.021842375 | 0.028669944 |
| BMX-68 | Toys | 2026 | [pmkao3g3](https://wandb.ai/baymaxam/GRID/runs/pmkao3g3) | 19412 | 0.034875335 | 0.054244797 | 0.022196151 | 0.028440854 |

全部最终Testing run均finished、exit0、recommendation_output Artifact COMMITTED。Beauty各22363用户、Sports各35598用户、Toys各19412用户；各seed完整用户集合一致，候选是对应完整商品目录内的原始item key，每行10个候选无重复。候选不滤历史、保留冷目标。逐用户独立first-match Recall/NDCG复算记录核验通过；仅纳入这九个有效最终run，不纳入首轮失败或已撤回的误执行CF test。

## 冻结协议与复现边界

独立LETTER-TIGER实现，作者代码定位commit为8d0154e28de37dbb6e24871c508ad8ddb1921cda。baseline_protocol=letter-official-grid-v1；CF=letter-cf-sasrec32-grid-v1；SID=letter-sinkhorn-prefix-assignment-v1；evaluation=full-catalog-no-history-filter-v1。输入为共同1024维内容向量和本seed独立32维CF；独立Tokenizer产生唯一四码SID。推荐为history20、temperature1、beam20/top10、FP32、两卡per-device batch128/global256、50000 optimizer steps、每500步完整evaluation，按val/ndcg@10最大选best，Testing使用同seed相同SID与固定best。无新增搜索预算。

CF teacher训练设置、step/NDCG选优与训练预算、温度1、容量内末层硬匹配及初始化n_jobs10均是已冻结的GRID适配，不声明逐项复现作者论文预算或数值。Beauty/Sports的Tokenizer早于diversity采样性能修复，Toys使用该修复；此前聚焦数值等价核验支持该修复，详见对应issue和优化验证记录。

历史来源限制继续保留：BMX-61/62/63的CF运行曾记录origin=mismatch，实际运行archive/manifest完整性及相关CF代码一致性已经核验；本次汇总不回填历史标记。last.ckpt可能仅位于最近best保存时刻，不能视作预算末尾恢复点；九组最终Testing都使用validation-selected best。后续阶段和最终Testing source origin verified；本轮回读最终源码SHA256均为45635c00cba54eb43df3582c163ebde52dce53130198d98f75a6df2cb552c2b9。

## 固定 checkpoint 与 SID

| Issue | 推荐训练run | 固定best checkpoint | 固定SID |
|---|---|---|---|
| BMX-60 | [diiyhjux](https://wandb.ai/baymaxam/GRID/runs/diiyhjux) | `wandb://baymaxam/GRID/diiyhjux?role=checkpoint&alias=v0&file=step_step=040500.ckpt` | `wandb://baymaxam/GRID/3fgw74y3?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt` |
| BMX-61 | [qzcesmm6](https://wandb.ai/baymaxam/GRID/runs/qzcesmm6) | `wandb://baymaxam/GRID/qzcesmm6?role=checkpoint&alias=v2&file=step_step=036500.ckpt` | `wandb://baymaxam/GRID/ilfqdvq3?role=semantic_id&alias=v1&file=merged_predictions_tensor.pt` |
| BMX-62 | [yfdhrh8g](https://wandb.ai/baymaxam/GRID/runs/yfdhrh8g) | `wandb://baymaxam/GRID/yfdhrh8g?role=checkpoint&alias=v1&file=step_step=038000.ckpt` | `wandb://baymaxam/GRID/842jwvqs?role=semantic_id&alias=v2&file=merged_predictions_tensor.pt` |
| BMX-63 | [0gokpcne](https://wandb.ai/baymaxam/GRID/runs/0gokpcne) | `wandb://baymaxam/GRID/0gokpcne?role=checkpoint&alias=v2&file=step_step=041500.ckpt` | `wandb://baymaxam/GRID/n19hvxe1?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt` |
| BMX-64 | [wdmgy3lu](https://wandb.ai/baymaxam/GRID/runs/wdmgy3lu) | `wandb://baymaxam/GRID/wdmgy3lu?role=checkpoint&alias=v1&file=step_step=039500.ckpt` | `wandb://baymaxam/GRID/7gbg8agr?role=semantic_id&alias=v1&file=merged_predictions_tensor.pt` |
| BMX-65 | [ktf4xvx1](https://wandb.ai/baymaxam/GRID/runs/ktf4xvx1) | `wandb://baymaxam/GRID/ktf4xvx1?role=checkpoint&alias=v0&file=step_step=043500.ckpt` | `wandb://baymaxam/GRID/1ec5jvzl?role=semantic_id&alias=v2&file=merged_predictions_tensor.pt` |
| BMX-66 | [6ihv78wr](https://wandb.ai/baymaxam/GRID/runs/6ihv78wr) | `wandb://baymaxam/GRID/6ihv78wr?role=checkpoint&alias=v0&file=step_step=041000.ckpt` | `wandb://baymaxam/GRID/3twcyb62?role=semantic_id&alias=v1&file=merged_predictions_tensor.pt` |
| BMX-67 | [whmg127q](https://wandb.ai/baymaxam/GRID/runs/whmg127q) | `wandb://baymaxam/GRID/whmg127q?role=checkpoint&alias=v1&file=step_step=043500.ckpt` | `wandb://baymaxam/GRID/side3vu5?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt` |
| BMX-68 | [ondvkww0](https://wandb.ai/baymaxam/GRID/runs/ondvkww0) | `wandb://baymaxam/GRID/ondvkww0?role=checkpoint&alias=v2&file=step_step=036500.ckpt` | `wandb://baymaxam/GRID/73tmpjqr?role=semantic_id&alias=v2&file=merged_predictions_tensor.pt` |

## 证据与完成核验

本轮核验UTC：`2026-10-10T06:46:48.018840+00:00`。通过wandb.Api对上述九组最终Testing和九组训练精确回读：finished/exit0、dataset/seed、冻结protocol、testing目录、generation参数、summary/用户数、消费固定checkpoint/SID、发布输出COMMITTED及文件digest、实际checkpoint SHA256与训练best文件一致、最终source origin verified。三数据集完整三seed，无重复或缺槽位，汇总数值从回读summary重新计算。

- 当前主表与来源清单：本地及node1 `logs/letter-main-table-20261010/verification.json`。
- Beauty/Sports逐用户独立审计：`logs/letter-testing-20261009-summaryfix/testing-verification.json`；SID lineage和训练完成审计沿用对应issue记录。结果解释见 [Beauty/Sports最终Testing](letter-beauty-sports-testing-20261009.md)。
- Toys逐用户独立审计：`logs/letter-toys-testing-20261010/testing-verification.json`；原始testing输入manifest、训练完成核验、完整命令与输出URI均保留。结果解释见 [Toys最终Testing](letter-toys-results-20261010.md)。
- 实现与适配说明：[LETTER运行协议](letter.md)。九个子issue保留全链路CF→Tokenizer→SID→推荐→Testing的固定引用、独立命令与逐阶段证据。

本父任务只完成LETTER主表汇总。其他方法的汇总和论文整体证据审查仍归各自任务；不以BMX-130完成替代五方法矩阵的联合审查。
