# IntRR M4 八格训练启动回执

## 授权与执行范围

用户于2026-10-19明确要求“在node1上启动intrr训练，使用tmux启动”，据此恢复原M4中未运行的八格训练：Beauty seeds200／2026、Sports和Toys seeds42／200／2026。Beauty42已有合规训练与Testing，继续复用，不重复运行。本批仅训练，关闭训练后自动Testing；八格预算为 **8次训练、400,000 optimizer steps**，不新增调参、seed、上游训练或Testing。

八格已在node1各建立独立tmux会话，使用同一串行队列，IntRR最大并发数为1。首格BMX-197于北京时间 **2026-10-19 22:50:04** 进入执行，当前为1格running、7格waiting_predecessor。物理GPU固定为 **0、7**，与我方既有BARS任务共享；未占用其他GPU。各格均保留DDP双进程与global batch256，不因串行调度改变实验配置。

## 本批身份与单元

- 提交时间：北京时间2026-10-19 22:47:48。
- node1仓库：`/data3/weizhenyu/projects/GRID`。
- 远端批次目录：`/data3/weizhenyu/projects/GRID/logs/intrr/m4_train_20261019_224718`。
- 批次标识：`intrr_m4_20261019_224718`。
- 单元命令、run directory及tmux完整身份：[batch.json](batch.json)。
- 逐单元观测状态、源码来源与输入摘要：[preflight-and-status.json](preflight-and-status.json)。

| 顺序 | Linear单元 | 数据集 | seed | W&B run | tmux session | DDP端口 | 当前阶段 |
|---:|---|---|---:|---|---|---:|---|
| 1 | [BMX-197](https://linear.app/baymax104/issue/BMX-197) | Beauty | 200 | [swu5s4wy](https://wandb.ai/baymaxam/GRID/runs/swu5s4wy) | `bmx-197-intrr-beauty200-20261019_224718` | 29853 | 首格执行 |
| 2 | [BMX-198](https://linear.app/baymax104/issue/BMX-198) | Beauty | 2026 | [ppg0xyqx](https://wandb.ai/baymaxam/GRID/runs/ppg0xyqx) | `bmx-198-intrr-beauty2026-20261019_224718` | 29854 | 排队 |
| 3 | [BMX-199](https://linear.app/baymax104/issue/BMX-199) | Sports | 42 | [dcgyc6s2](https://wandb.ai/baymaxam/GRID/runs/dcgyc6s2) | `bmx-199-intrr-sports42-20261019_224718` | 29855 | 排队 |
| 4 | [BMX-200](https://linear.app/baymax104/issue/BMX-200) | Sports | 200 | [t36o8gnd](https://wandb.ai/baymaxam/GRID/runs/t36o8gnd) | `bmx-200-intrr-sports200-20261019_224718` | 29856 | 排队 |
| 5 | [BMX-201](https://linear.app/baymax104/issue/BMX-201) | Sports | 2026 | [htszjufh](https://wandb.ai/baymaxam/GRID/runs/htszjufh) | `bmx-201-intrr-sports2026-20261019_224718` | 29857 | 排队 |
| 6 | [BMX-202](https://linear.app/baymax104/issue/BMX-202) | Toys | 42 | [6ismz9td](https://wandb.ai/baymaxam/GRID/runs/6ismz9td) | `bmx-202-intrr-toys42-20261019_224718` | 29858 | 排队 |
| 7 | [BMX-203](https://linear.app/baymax104/issue/BMX-203) | Toys | 200 | [kie5uzi5](https://wandb.ai/baymaxam/GRID/runs/kie5uzi5) | `bmx-203-intrr-toys200-20261019_224718` | 29859 | 排队 |
| 8 | [BMX-204](https://linear.app/baymax104/issue/BMX-204) | Toys | 2026 | [keeshepi](https://wandb.ai/baymaxam/GRID/runs/keeshepi) | `bmx-204-intrr-toys2026-20261019_224718` | 29860 | 排队 |

排队单元的run ID已固定；其W&B记录由对应训练实际进入时建立，不能仅凭预分配链接视为训练已启动。上表是本次交接时点的阶段快照。

## 固定协议与来源

通用配置沿用用户选定的TIGER参照和 `intrr-shared-ran-tiger-v1`：固定TFRecord划分与RKMeans SID，180 SID slots／最多44件历史商品，TIGER连续子序列增强最多32条；scratch、FP32、DDP2、train batch128/卡、validation batch64/卡、workers32/16、gradient accumulation1；Adam lr0.0005、weight decay0.000001，无scheduler和early stopping。每格50,000 optimizer steps，每100步验证、每50步记日志，以自身最高 `val/ndcg@10` 保存top1，若并列取首次。

IntRR内部参数保持UID512→模型256、共享RAN hidden512、STE、4层causal T5、6 heads／d_kv64、FF1024、dropout0.15、temperature1、alignment0.1和合法SID beam10。作者来源commit为 `806e0f1969ed61a0748902649b335c0ea066de00`；完整训练及后续Testing验收协议见[原M4计划](../../intrr-m4-plan-20261019.md)。

固定SID producers为Beauty `dq77e3wo`、Sports `jcyr5l3p`、Toys `3dycz43g`，均使用 `v0`、`merged_predictions_tensor.pt`。三数据集各split分别为175／279／152份，共1,818份TFRecord分片已进行逐文件hash核准；全部清单保留于远端批次目录 `preflight.json`。本地[输入摘要](preflight-and-status.json)保留九个split的文件数、字节数和聚合SHA256，以及三份SID Artifact digest和compact catalog SHA256。

本批源码快照包含320个文件，SHA256为 `390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4`，source origin的 `status=verified`、`git_authority=local-workspace`。首格归档SHA256为 `3781a5c150f3adf5b6f6b0c71f09a82c2c1d1f1a3962582fa1680df509a0088f`，归档内320文件已逐字节核准。代码交接通过受管Mutagen同步完成，不以远端Git状态判断版本。启动前67项聚焦测试通过。

## 启动核验

首格BMX-197的[启动审计](startup-audit.json)于北京时间 **2026-10-19 22:51:44** 通过。W&B为 `running`，group为 `paper_main_intrr_beauty`，实际resolved config逐字段核准50k、FP32、DDP2、batch128/64、workers32/16、Adam、无scheduler、无QA limit flags和关闭自动Testing。

| 核验对象 | 实测快照 |
|---|---|
| W&B `trainer/global_step` | 299；日志步轴少1 |
| train/loss | 30.98035049438477 |
| val/loss | 22.256275177001953 |
| val/ndcg@10 | 0.0044416943565011024 |
| val/recall@10 | 0.007823553867638111 |
| 启动checkpoint | `checkpoint_epoch=000_step=000200.ckpt`，`global_step=200` |
| checkpoint SHA256 | `e6b2884f93cc00312a760de9776bd578b64f1a7a8e47fb580d8c17291e52b89e` |
| optimizer与浮点张量 | 全部Adam states的step为200；checkpoint浮点张量均有限 |
| UID table | `[12101,512]` |
| DDP身份 | rank0 PID3201187→物理GPU0；rank1 PID3201188→物理GPU7；WORLD_SIZE=2 |
| 来源与lineage | source archive全部文件核验通过、origin verified，Beauty SID Artifact digest与preflight一致 |

上述loss与指标均为有限值。W&B日志299和checkpoint200来自不同读取时点；checkpoint200用于证明参数真实更新，其不构成最终own-best。该审计仅读取既有正式训练产物，没有额外模型forward或训练。本批尚无新增Testing结果。

首次队列guard执行时缺少项目import路径，在任何模型forward之前退出。已修复guard的import路径，以同一批次和相同八个run ID继续；原failure档案保留。此事件未消费模型forward或optimizer step，不计训练重试或新增实验预算。

## 监测与产物保留

从本地查看首格tmux：

```powershell
ssh node1 "tmux capture-pane -p -t bmx-197-intrr-beauty200-20261019_224718 -S -80"
```

交互查看：

```bash
cd /data3/weizhenyu/projects/GRID
tmux attach -t bmx-197-intrr-beauty200-20261019_224718
```

每格的resolved config、source snapshot、数据与SID来源、正式console日志、checkpoint、W&B记录及退出身份均保留于其run directory。批次队列状态和guard修复前failure档案保留于上述远端批次目录。接入阶段dry-run／5step临时记录的清理要求不适用于本次正式训练产物。训练结束后仍须核准50k／500次验证、own-best checkpoint身份，再单独执行并审计Testing，方可将对应M4单元记为Done。
