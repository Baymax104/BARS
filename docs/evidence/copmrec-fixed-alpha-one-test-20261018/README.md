# CoPMRec 固定 alpha=1 的正式 Testing

2026-10-18，按用户指令在 node1 使用 tmux 执行 Beauty / seed42 / `fixed_alpha_one` 的单卡 Testing。推理于北京时间 13:20:55 完成，退出码为0，共输出22,363行预测。

训练 run 为 [lwtzxzre](https://wandb.ai/baymaxam/GRID/runs/lwtzxzre)，Testing run 为 [2n4nydm6](https://wandb.ai/baymaxam/GRID/runs/2n4nydm6)。训练完整达到50,000步，100次 Validation 中首次最优点为47,500步，`val/ndcg@10=0.05225898697972298`。本次加载该自身最优 checkpoint，SHA256 为 `208b78fb8b9c21ee84e78214fd6b940fba9cfecb28e6699afd1c5440a869d406`。

沿用正式协议：全目录 dense Top10、无历史排除、cold 商品可参与。训练精确固定 alpha=1，保留三目标，gate 冻结。hybrid 仍处于探索阶段，本次没有变更正式部署协议。

## 已核验结果

| 指标 | 可学习 Full | 固定 alpha=1 | 固定臂相对变化 |
| --- | ---: | ---: | ---: |
| Recall@5 | 0.04807047 | 0.04699727 | -2.23% |
| NDCG@5 | 0.03194638 | 0.03093107 | -3.18% |
| Recall@10 | 0.07208335 | 0.07226222 | +0.25% |
| NDCG@10 | 0.03967084 | 0.03905669 | -1.55% |

预定主要指标 NDCG@10 的差值为 `fixed−Full=-0.0006141491`，PCG64 / seed42 / 2,000次用户配对 bootstrap 的95%区间为 `[-0.0014707402, 0.0002662724]`，跨零。NDCG@5 差值区间为 `[-0.0019172339, -0.0000942813]`，该 pointwise 区间未跨零。该单元表现为指标权衡，尚不足以确认预定主要指标上的差异；不能称两臂等价，也不能单独归因为 gate 是否可学习。

独立审计通过：22,363名用户的真实标签身份与 Full 完全一致，Top10 无非法或重复商品，四指标复算与 W&B 的误差均小于 `1e-8`。源归档297个文件与本地工作区逐项一致，checkpoint 身份、上游 SID/content digest 和 Artifact lineage 均通过。审计仅复算已有预测，没有新增模型 forward。

预测产物为 `copmrec_v2_beauty_seed42_fixed_alpha_one_inference-recommendation-output:v0`，SHA256 为 `b13ccb6d623155d0b27c73cf8531865af7c118c9afdac5ee2111347e0280a048`。完整四指标、配对区间、seen/cold、训练词频及历史长度切片见 [audit.json](audit.json)。

研究计划与状态已同步为 `completed_audit_passed`，本补充预算1次50k训练与1次Testing闭环，当前v2累计完成650k。[BMX-166](https://linear.app/baymax104/issue/BMX-166/copmrec-v2-增补-固定-alpha1-vs-可学习混合beauty-seed42)已更新为Done并回读验证；项目、M3 milestone和标签保持。

## 执行证据

- [实际启动脚本](launch.sh)、[分发回执](launch-receipt.json)、[完成回执](completion.json)。
- [训练完成、选点与 checkpoint 核验](training-verification.json)。
- [独立复算脚本](audit.py)、[复算及用户配对统计](audit.json)、[本地源码逐文件来源核验](local-origin-verification.json)。
- [补充实验协议与结果](../../../../research/docs/copmrec-v2-fixed-alpha-one-plan-20261018.md)。

tmux session 为 `bmx-166-alpha1-test-20261018-1318`，使用物理GPU7、逻辑设备`[0]`。远端目录为 `/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-166_test_20261018_1318`，包含 `console.log`、`exit_code`、Hydra配置、源码快照及标准 `{keys, predictions}` 输出。

交付远端前已执行 Mutagen flush，三个 session 均为 `Watching for changes`、无 conflict，并核验8个直接相关文件本地/远端 SHA256 一致。使用原 `.venv`、`UV_NO_SYNC=1` 和既有统一入口；未修改依赖。没有设置持续监控、自动重跑或追加实验。
