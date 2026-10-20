# LETTER Toys SID 导出与推荐训练（2026-10-10）

后续更新（2026-10-10）：三组推荐训练及最终Testing已完成并独立核验，BMX-66～68已Done。正式结果见 [LETTER Toys 最终结果](letter-toys-results-20261010.md)；下文保留历史启动快照。

## 推荐训练启动核验快照

核验UTC：`2026-10-10T04:05:36.043065+00:00`。W&B running、实际step>0、loss有限、两卡DDP初始化、固定SID消费lineage、冻结配置、source Artifact COMMITTED及源码archive SHA256核验通过。无Traceback/OOM或exit文件。

| seed | step | train/loss |
|---:|---:|---:|
| 42 | 499 | 6.121185 |
| 200 | 499 | 6.170124 |
| 2026 | 499 | 5.860004 |

BMX-66～68已更新当前状态、固定SID/推荐命令及完整阶段证据，保持In Progress。该快照只证明启动；最终完成和Testing仍需重新查询。

用户在三组Tokenizer训练完成后授权继续，执行Tokenizer完成核验、SID导出与独立审计，再启动推荐训练。

## Tokenizer 完成核验

三组均finished、exit0，20000 epoch完成（最终W&B epoch19999、最后记录optimizer step239999），共10次完整目录collision_rate验证。下游使用val/collision_rate最小选择的best；验证记录最小值、checkpoint callback分数、Artifact selection/monitor/mode及实际读取文件SHA256一致。

| Issue | seed | Tokenizer run | best step | best collision_rate |
|---|---:|---|---:|---:|
| BMX-66 | 42 | [c6pirdxb](https://wandb.ai/baymaxam/GRID/runs/c6pirdxb) | 240000 | 0.006876887 |
| BMX-67 | 200 | [kiqf0416](https://wandb.ai/baymaxam/GRID/runs/kiqf0416) | 96000 | 0.006876887 |
| BMX-68 | 2026 | [dcv99aeo](https://wandb.ai/baymaxam/GRID/runs/dcv99aeo) | 48000 | 0.007715532 |

- BMX-66固定best：`wandb://baymaxam/GRID/c6pirdxb?role=checkpoint&alias=v1&file=step_step=240000.ckpt`；SHA256=`0886ebf27c78e98d8459e014950ab0979ff1be0408a0b8e3593bff866d91a163`。
- BMX-67固定best：`wandb://baymaxam/GRID/kiqf0416?role=checkpoint&alias=v2&file=step_step=096000.ckpt`；SHA256=`9e471625cd3a3ae05abfcadb3db456fe354e03e138d734abab1dbe4a0e5bc4d3`。
- BMX-68固定best：`wandb://baymaxam/GRID/dcv99aeo?role=checkpoint&alias=v0&file=step_step=048000.ckpt`；SHA256=`fb03f785e3b54442e4fa9641610f6ee0de332cf756521bcae9e24d285c44b3a9`。

完成状态以W&B全程记录及exit0核验；不能把last.ckpt视为最终step，后两组last实际位于各自best保存时刻，本次均使用固定best。

## SID 审计

三组导出run均finished、exit0，semantic_id Artifact均COMMITTED。完整bundle含keys/predictions，覆盖11924商品，四码整数范围[0,256)，完整SID全局唯一、keys与内容/CF目录一致；同GPU/medium精度下原始编码前三码未改变。最大prefix人口分别47、47、48，小于末层容量256；本地writer与Artifact输出逐元素一致，发布文件digest、实际checkpoint SHA256、输入及source lineage核验通过。

| Issue | SID run | 固定Artifact | 最大prefix人口 |
|---|---|---|---:|
| BMX-66 | [3twcyb62](https://wandb.ai/baymaxam/GRID/runs/3twcyb62) | letter_sid_toys-semantic-id:v1 | 47 |
| BMX-67 | [side3vu5](https://wandb.ai/baymaxam/GRID/runs/side3vu5) | letter_sid_toys-semantic-id:v0 | 47 |
| BMX-68 | [73tmpjqr](https://wandb.ai/baymaxam/GRID/runs/73tmpjqr) | letter_sid_toys-semantic-id:v2 | 48 |

- BMX-66固定SID：`wandb://baymaxam/GRID/3twcyb62?role=semantic_id&alias=v1&file=merged_predictions_tensor.pt`；bundle SHA256=`373c32eeb5b9235a70000e32773ef3f4f0264f7932dbc74a75e83a61a1174b7c`。
- BMX-67固定SID：`wandb://baymaxam/GRID/side3vu5?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt`；bundle SHA256=`1c695001397ee6b08a885e1ed27426d4bb6b838327b62f4c1382565c8e987c2e`。
- BMX-68固定SID：`wandb://baymaxam/GRID/73tmpjqr?role=semantic_id&alias=v2&file=merged_predictions_tensor.pt`；bundle SHA256=`a348830510e511a51b3e43bcdf6ff71a6e033a721ac10465da1a9d255c1c5e93`。

## 推荐训练分配

| Issue | seed | 物理GPU → 逻辑CUDA | port | W&B run | tmux |
|---|---:|---|---:|---|---|
| BMX-66 | 42 | 0,1 → 0,1 | 30466 | [6ihv78wr](https://wandb.ai/baymaxam/GRID/runs/6ihv78wr) | `letter_train_bmx66_toys_s42_6ihv78wr` |
| BMX-67 | 200 | 2,3 → 0,1 | 30467 | [whmg127q](https://wandb.ai/baymaxam/GRID/runs/whmg127q) | `letter_train_bmx67_toys_s200_whmg127q` |
| BMX-68 | 2026 | 4,5 → 0,1 | 30468 | [ondvkww0](https://wandb.ai/baymaxam/GRID/runs/ondvkww0) | `letter_train_bmx68_toys_s2026_ondvkww0` |

两卡DDP、FP32、每卡batch128/global256、accumulation1、50000 optimizer steps，每500步完整evaluation；val/ndcg@10最大选best，history20、beam20/top10、无历史过滤，固定AdamW/warmup/cosine协议，run_test_after_training=false。训练独立消费本seed固定SID。分配时GPU5存在其他任务，显存余量充足；保留既有任务。

## 来源与运行记录

执行前Mutagen flush成功，三个session均Watching for changes、无conflict。运行源码source SHA256=`45635c00cba54eb43df3582c163ebde52dce53130198d98f75a6df2cb552c2b9`，source origin verified。源码未在本轮修改，使用此前Tokenizer与prefix性能修复。

node1仓库根目录：`/data3/weizhenyu/projects/GRID`。证据目录：`logs/letter-toys-pipeline-20261010/`，本地保留同路径JSON副本，包含tokenizer-completion.json、sid-plan.json、sid-verification.json、training-plan.json及后续training-startup.json。远端各阶段独立tmux、log和exit文件，脚本通过bash -n。

```bash
tmux attach -t letter_train_bmx66_toys_s42_6ihv78wr
tmux attach -t letter_train_bmx67_toys_s200_whmg127q
tmux attach -t letter_train_bmx68_toys_s2026_ondvkww0
```

本轮执行边界为SID完成及推荐训练启动；推荐训练最终50k完成与Testing仍需单独核验。
