# BARS M2：hybrid Validation 九格重启

用户于2026-10-22明确要求按hybrid Validation选点并重启M2；若Beauty/seed42也采用dense选点，则一并重训。实际W&B配置确认 `qtyamris` 的evaluation_mode/prediction_mode均为dense，因此本批九格全部从scratch训练，原1/9覆盖不计入新hybrid选点矩阵。

## 旧队列停止与历史成本

旧批次八个tmux已于北京时间02:09:25全部停止；从队尾先取消排队任务，再停止实际训练，逐格核验后代进程退出和session消失。旧 `eui0uqas` 停止前最后读取的W&B step为18399，这是最后已记录进度，不声明为精确终止更新数；其余七格尚未启动。日志、checkpoint、W&B来源和既有Beauty42的50k训练/测试结果保留，实际已耗成本不清零、不重算为400k。详见[cancellation.json](cancellation.json)。

## 新九格与状态

2026-10-22 02:22:05（北京时间）已在node1提交九个独立tmux。物理GPU4/5、逻辑[0,1]、DDP2单队列：209→186→187→188→189→190→191→192→193。每格50k，共450k授权训练；无自动Testing、额外smoke、独立Validation、上游重跑、额外seed或调参。

| Linear | 数据集 | seed | 新训练run ID | MASTER_PORT |
| --- | --- | ---: | --- | ---: |
| BMX-209 | beauty | 42 | `httwyhka` | 31300 |
| BMX-186 | beauty | 200 | `63whsx9s` | 31301 |
| BMX-187 | beauty | 2026 | `uotmewdu` | 31302 |
| BMX-188 | sports | 42 | `op60l871` | 31303 |
| BMX-189 | sports | 200 | `ubr7izg9` | 31304 |
| BMX-190 | sports | 2026 | `4c00jwid` | 31305 |
| BMX-191 | toys | 42 | `0yi4zt92` | 31306 |
| BMX-192 | toys | 200 | `576pc4tq` | 31307 |
| BMX-193 | toys | 2026 | `wis7tks0` | 31308 |

排队ID为预留身份，实际开始才创建W&B run。状态以[startup-status.json](startup-status.json)、[wandb-startup.json](wandb-startup.json)的观察时间为准；完整预测结果的已验收覆盖当前为0/9，启动与checkpoint存在不算完整训练或最终结果验收。

02:25:50已读取真实step500 checkpoint并通过零forward审计：training_validation为`hybrid_beam_plus_all_cold`，validation_retrieval明确beam20、全部cold、目录logits稳定Top10且无历史排除；loss1/1/0、frozen_0.5、双残差与所有Adam moments的step500一致，实际源码origin=verified。checkpoint SHA256为`144d78f15e989b80145b1dad28ca078862c4247b56e4e73b80dd3d15e0056547`，完整契约见[checkpoint-startup.json](checkpoint-startup.json)。

## 实际选择协议

当前主变体为`untied_fixed_alpha_half_no_mixture`，固定alpha=0.5、双残差、SID CE/Catalog CE/mixture NLL权重1/1/0。主版本component默认hybrid，九格实际命令另显式设置：

```text
model.root.validation_selection_mode=hybrid
model.root.evaluation_mode=hybrid
model.root.prediction_mode=hybrid
```

每500更新进行hybrid Validation：等权混合概率生成beam20，并入全部cold商品，使用原目录logits、按catalog row稳定排序取Top10，无历史排除。按本格首次最高val/ndcg@10选点；训练目标、AdamW base/residual LR=0.0003/0.002、wd0.035、warm2500/cosine50000、global256/FP32、clip1保持。训练的目录CE及验证loss仍计算全目录分母，不等于使用dense排名选点。

ScratchTrainingProtocol实际eval_step已从硬编码dense改为显式选择模式。新checkpoint记录`training_validation=hybrid_beam_plus_all_cold`、完整validation_retrieval和一致hybrid部署身份；dense与hybrid的checkpoint不能交叉恢复。旧dense契约保持兼容，历史复验须显式使用dense选择身份。新九格全部`ckpt_path=null`。

## 验证与同步

- 124个不同的聚焦用例全部通过：首次121通过、3个旧错误文案匹配失败，修正兼容文案后6项定向复验通过；最终checkpoint契约改动后30项候选行为、旧dense兼容及恢复边界回归通过。详见[local-verification.json](local-verification.json)。
- 真实hybrid候选验证用例检查高分但未生成的seen商品不会从全目录补入，cold并集、历史可选、稳定排序及validation/prediction一致。
- 九格实际root-script argv、Hydra compose/resolve、bash语法与完整协议检查通过，preflight没有模型forward。OpenSpec strict、Ruff和相关diff检查通过。
- Mutagen flush成功，三个session均Watching、无冲突。323份受管源码与可信本地一致：`cc2a911330f089f71e63916616f05859da976d3699dd7a1e42c219b25eceda6a`。
- 1818份TFRecord逐文件path/size/SHA、六个上游Artifact name/digest、三数据集目录和seen-mask全部匹配冻结来源。详见[preflight.json](preflight.json)。

每格只有在前驱exit0、源码哈希一致，以及两卡各至少24GiB空余、连续三次低于10%利用率后才启动；资源不满足就等待，不终止其他任务。失败或源码漂移停止后继，不自动重试训练。训练exit0仅标为finished_pending_audit，随后仍需验收50k、100次Validation和最终自身best来源。

## 查看与证据

```powershell
ssh -t node1 'tmux attach -t bmx-209-bars-hybrid-beauty42-20261022_021600'
```

远端批次：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_hybrid_selection_20261022_021600`；各格输出为`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-<编号>_hybrid_train_20261022_021600`。Ctrl-b、d分离后任务继续运行。

完整实际命令和身份见[batch.json](batch.json)；提交回执见[launch-receipt.json](launch-receipt.json)。首个hybrid checkpoint的零forward审计保存于`checkpoint-startup.json`，它是启动验证，不是50k后的最终own-best验收。Linear和研究状态使用本次hybrid九格记录，旧dense说明整体保留为历史来源。
