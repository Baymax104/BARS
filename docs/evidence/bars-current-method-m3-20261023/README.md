# 当前方法 M3：回退、预检与有界队列提交回执

日期：2026-10-23，北京时间。协议：`bars-fixed-half-hybrid-m3-20261023-v1`。本页最新观察为02:39:00：当前状态 `mechanism_running_training_queued`，C实际W&B已running，三条训练均queued、实际启动0、完成0；正式机制及新消融结果均未验收。三次正式own-best Testing未授权、未排队、未执行。

## 授权与固定范围

用户要求按当前方法重做机制与消融实验、回退Linear M3，并确认沿用Beauty／seed42。复用当前Full `httwyhka` own-best46000与正式预测 `prt5r0v5`；新Shared、双侧零残差、去Catalog CE各scratch50k，共150k。固定alpha0.5，前两臂loss1/1/0、去CE为1/0/0；100次hybrid Validation及各自首次最高val/NDCG@10选点。执行计划与结果分支见[统一计划](../../bars-current-method-m3-plan-20261023.md)。

本次只提交C固定模型诊断及上述三训练，Testing仍为训练验收后的独立授权步骤。未重复Full训练或推荐Testing，未扩数据集／seed、上游、扫描、默认smoke或自动重试。

## Linear回退与清理

完整快照见[原M3](linear-before.json)、[补充旧卡](linear-additional-before.json)，逐项操作见[计划](linear-m3-plan.json)、[写回](linear-writes.json)、[清理回读](linear-readback.json)、[清理验证](linear-verification.json)及[最终回读](linear-final.json)。原M3的100%完成状态已回退；启动前五项均Todo。最终回读194仅实现准备Done、205和208 In Progress、206和207 Todo queued，正式结果仍0；M2当前父项及九个单元仍全部Done。

BMX-168、170至178及184共11个过时卡已退出项目与里程碑，回读确认两字段为空，保留原Done、父子关系及原来源描述。当前连接器没有issue删除接口，因此本次未物理删除；未删除W&B、Artifact、checkpoint或本地历史报告。

## 实现与远端预检

本地133项聚焦检查通过，1项因Windows Gloo跳过；node1实际双rank三条新臂CPU检查均通过，验证零残差冻结和去CE目录表零梯度／Adam恢复等执行契约。汇总见[本地与远端验证](local-verification.json)，远端原件见[双rank stdout](ddp-check.stdout)及[stderr](ddp-check.stderr)。

[训练预检](preflight.json)与[C机制预检](mechanism-preflight.json)通过：323份源码与可信本地来源一致、Beauty三split共525个TFRecord逐文件校验、四组真实脚本argv/Hydra compose/bash语法、目录和seen-mask、当前Full checkpoint与冻结预测URI/SHA均匹配。C预检新增模型forward、optimizer更新和W&B run均为0；预检不计正式结果。

本批源码SHA256：`a36cc767699fc22d932c5af8765f09032904e56e39f5d12e2959662836e75827`。输入、命令、来源快照和各自wrapper全部保存在[batch.json](batch.json)；Mutagen flush及三session Watching由本轮提交前核验。

## 实际提交与当前运行

北京时间02:37:07已提交四个独立tmux，单槽按C→Shared→Zero→noCE串行；前驱失败或来源漂移停止，不自动重试。各任务启动前再次检查来源、GPU连续三次低利用率及每卡至少24GiB余量，不终止已有服务。C使用物理GPU4，训练使用GPU4/5、DDP2。

远端批次目录：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m3_current_20261023_023410`。

| 任务 | run身份 | tmux | 最新观察 |
| --- | --- | --- | --- |
| C／BMX-208 | 实际 `gkwknl0l` | `bmx-208-m3-generation-20261023_023410` | W&B running，配置及来源核验通过，正式结果待审计 |
| Shared／BMX-206 | 预留 `gu3l2s2s` | `bmx-206-m3-shared-20261023_023410` | queued，尚无实际训练更新 |
| Zero／BMX-206 | 预留 `1k2ebqaw` | `bmx-206-m3-zero-20261023_023410` | queued，尚无实际训练更新 |
| noCE／BMX-207 | 预留 `7u93dubs` | `bmx-207-m3-noce-20261023_023410` | queued，尚无实际训练更新 |

C于02:37:18启动进程，02:38开始analysis；首次W&B查询run不存在属于初始化时点。02:39:00已核实[实际W&B](https://wandb.ai/baymaxam/GRID/runs/gkwknl0l)为running、group=`mechanism_main`，resolved config中的当前协议、固定alpha0.5、hybrid、checkpoint／预测URI均正确；四项上游Artifact lineage齐全，源码origin verified。尚无正式汇总指标，不将运行或初始化验收计为production复现、四臂完成或机制结论。

提交及观察原件：[launch-receipt.json](launch-receipt.json)、[startup-status.json](startup-status.json)、[wandb-startup.json](wandb-startup.json)。预留训练ID只代表排队身份；W&B实际创建和更新须后续独立核验。

## 账本与后续门禁

新增训练预算150k、已提交3／实际启动0／完成0／已记录更新0；C诊断已启动、不增加训练。新对照正式结果覆盖0/3，Testing计划3／授权0／提交0／完成0；冻结预测贡献等待三个新对照的正式结果。每臂训练50k／100val／首次自身best URI及SHA审计后，仍需用户另行明确授权Testing。

旧2026-10-19 M3及其750k账本、M2九格和独立预算完整保留。文档修改前的[历史基线](documentation-baseline.json)和[准备阶段验证](documentation-verification.json)保留原观察时点；后续提交状态核验另存新回执，不覆盖这两份历史快照。本轮不改论文，不以实现准备Done或已提交队列替代正式结果验收。
