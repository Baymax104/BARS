# LETTER Toys 正式训练与最终 Testing（2026-10-10）

BMX-66～68 的CF teacher、CF导出、Tokenizer训练、SID导出、推荐训练及最终Testing全部完成。三组Testing均finished、exit0，覆盖完整19412名用户；输出bundle、固定checkpoint/SID、输入及源码lineage与独立指标复算均通过，issue已更新Done。

## 最终 Testing 指标

| seed | Testing run | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
|---:|---|---:|---:|---:|---:|
| 42 | [jeslrexe](https://wandb.ai/baymaxam/GRID/runs/jeslrexe) | 0.034154131 | 0.053472079 | 0.022769337 | 0.028977509 |
| 200 | [yn904aco](https://wandb.ai/baymaxam/GRID/runs/yn904aco) | 0.033381414 | 0.054605399 | 0.021842375 | 0.028669944 |
| 2026 | [pmkao3g3](https://wandb.ai/baymaxam/GRID/runs/pmkao3g3) | 0.034875335 | 0.054244797 | 0.022196151 | 0.028440854 |
| 均值 | 三个seed | 0.034136960 | 0.054107425 | 0.022269287 | 0.028696102 |
| 样本标准差 | ddof=1 | 0.000747109 | 0.000579014 | 0.000467789 | 0.000269282 |

指标均为原始比例，未乘100。结果取自baymaxam/GRID对应Testing run的test/recall@5、test/recall@10、test/ndcg@5、test/ndcg@10 summary，并由原始testing目标与逐用户预测独立复算；误差≤1e-12。

## 推荐训练完成与选优

训练均finished、exit0，max_steps=50000到达、100次evaluation；W&B最后记录trainer/global_step=49999。只按val/ndcg@10最大值选best，不按Testing重新选优。历史最大值、checkpoint callback分数、Artifact selection/monitor/mode及实际文件SHA256一致。各阶段last.ckpt仅用于恢复，不作为本次Testing输入。

| Issue | 训练run | best step | best val/NDCG@10 | 固定best |
|---|---|---:|---:|---|
| BMX-66 | [6ihv78wr](https://wandb.ai/baymaxam/GRID/runs/6ihv78wr) | 41000 | 0.039514487 | `wandb://baymaxam/GRID/6ihv78wr?role=checkpoint&alias=v0&file=step_step=041000.ckpt` |
| BMX-67 | [whmg127q](https://wandb.ai/baymaxam/GRID/runs/whmg127q) | 43500 | 0.041076653 | `wandb://baymaxam/GRID/whmg127q?role=checkpoint&alias=v1&file=step_step=043500.ckpt` |
| BMX-68 | [ondvkww0](https://wandb.ai/baymaxam/GRID/runs/ondvkww0) | 36500 | 0.041415831 | `wandb://baymaxam/GRID/ondvkww0?role=checkpoint&alias=v2&file=step_step=036500.ckpt` |

## 独立核验与来源

核验UTC：`2026-10-10T06:22:56.057150+00:00`。读取152个原始testing TFRecord文件，19412唯一用户及各自末项目标；全量输出为keys/predictions bundle，shape=[19412,10]。按用户key对齐后，本地writer与Artifact writer输出逐元素相同；合并行顺序不作为身份依据。每个候选均为原始商品key且属于固定11924商品目录，每行10个候选无重复。全部用户及冷目标保留；逐用户first-match Recall/NDCG复算与W&B一致。

两卡DDP、FP32、完整目录Trie、history20、beam20/top10、无历史过滤。Testing使用统一src.main/letter_inference入口、testing目录及本seed训练相同SID，datamodule无训练数据加载器。实际加载checkpoint SHA256及checkpoint的SID目录身份一致；消费对应固定checkpoint/SID Artifact，发布文件digest核验通过。Source Artifact COMMITTED，origin verified，source SHA256=`45635c00cba54eb43df3582c163ebde52dce53130198d98f75a6df2cb552c2b9`；archive和所有288个源码条目SHA256核验通过。交付前Mutagen flush成功、三session Watching for changes无conflict，未修改训练代码或环境。

- BMX-66：checkpoint SHA256=`b7413ad1a2149ed3f7c13180563417f808e8689f1f585dcfaee3b075fb272ca3`；Testing Artifact=`letter_inference_toys-recommendation-output:v0`，bundle SHA256=`89fc350618053d46c02ab31376053ce74f488cb07cdb7e63a2bf065b242e6d76`；固定输出=`wandb://baymaxam/GRID/jeslrexe?role=recommendation_output&alias=v0&file=merged_predictions_tensor.pt`。
- BMX-67：checkpoint SHA256=`4007006a984e16857079220800fb7b56f325e6f83c3c6352efef4691967b6ce4`；Testing Artifact=`letter_inference_toys-recommendation-output:v1`，bundle SHA256=`7237c5670e5f4ca6058832cf0af2fb5cc5e7077035b6deb4554c400b73089fc3`；固定输出=`wandb://baymaxam/GRID/yn904aco?role=recommendation_output&alias=v1&file=merged_predictions_tensor.pt`。
- BMX-68：checkpoint SHA256=`44f3bf25cee6c466d976fcc05a5b5e7aa934790ab6edff4850640a59e13d0485`；Testing Artifact=`letter_inference_toys-recommendation-output:v2`，bundle SHA256=`f68e73416632007f05f2e0ac5fafd7690bc372738018074651edb3edb3dac5e9`；固定输出=`wandb://baymaxam/GRID/pmkao3g3?role=recommendation_output&alias=v2&file=merged_predictions_tensor.pt`。

## 复现命令与运行记录

node1仓库根目录：`/data3/weizhenyu/projects/GRID`。精确命令、notes、固定URI、GPU/port、log/exit及输出目录见 `logs/letter-toys-testing-20261010/testing-plan.json`，对应启动脚本test-bmx66.sh、test-bmx67.sh、test-bmx68.sh均通过bash -n。Testing会话保留，三组物理GPU分别1,3 / 6,7 / 4,5，port30566 / 30567 / 30568。

```bash
tmux attach -t letter_test_bmx66_toys_s42_jeslrexe
tmux attach -t letter_test_bmx67_toys_s200_yn904aco
tmux attach -t letter_test_bmx68_toys_s2026_pmkao3g3
```

完整证据位于node1及本地 `logs/letter-toys-testing-20261010/`：recommendation-completion.json、testing-plan.json、testing-input-manifest.json、testing-verification.json。原始testing数据清单SHA256=`39405d27035aadafdd601c475f5edf4b11d123384beefb59f9369c3a16f7c27f`。上游证据见 `docs/letter-toys-cf-export-20261009.md`、`docs/letter-toys-tokenizer-launch-20261009.md`、`docs/letter-toys-recommendation-launch-20261010.md` 及对应logs中的逐阶段核验。
