# BARS（CoPMRec v2）当前方法与运行入口

更新：2026-10-20。按用户决定，**BARS Untied 上位为当前主方法，BARS Shared 保留为共享残差对照**。实现命名继续使用 `copmrec`；W&B 的 run 显示名与 group 按本轮授权统一使用 `bars`，run ID、checkpoint、Artifact 与执行时来源身份保持。方法角色、实验状态和预算以[当前计划](../../research/ideas/current-plan.md)为准。

## 当前方法与证据范围

Untied 在历史侧和目录侧使用两张独立、零初始化的128维商品残差表，内容投影继续共享。历史表示使用 `P(c_i) + r_i^hist`，目录评分使用 `P(c_i) + r_i^cat`；两表均使用残差LR0.002，cold残差恒零。Shared 使用同一张商品残差表。两者均联合优化等权的 SID CE、joint catalog CE、mixture NLL，使用 learned global alpha，无 native view，所有阶段均不排除历史商品。

两种模型都由目录商品 posterior 聚合合法前缀 mass，与 decoder 概率混合生成20条 beam 候选；过滤非法SID、并入全部cold商品并去重后，按同一joint catalog logits与稳定catalog-row规则输出Top10。历史侧与目录侧的商品 residual 是否共享，是本次方法角色调整的差异；目录posterior贯通生成与排序的链路保持不变。当前实现仍计算全目录logits/prefix mass，不据此提出效率改善主张。

| 方法角色 | 已完成证据 | 当前执行入口与原始身份 |
| --- | --- | --- |
| **BARS Untied：主方法** | 三数据集×三seed的9格50k训练与自身own-best hybrid Testing全部完成并独立验收；另有Beauty42机制与贡献结果 | `copmrec_ablation_train.sh` / `copmrec_ablation_inference.sh --variant untied_residual`；`CoPMRecAblation`，`variant=untied_residual` |
| **BARS Shared：共享残差对照** | 既有三数据集×三seed的9格训练／hybrid Testing矩阵，以及原Shared系统消融与机制分析 | `copmrec_train.sh` / `copmrec_inference.sh`；`CoPMRec`，历史 Full 身份保持 |

Untied训练为[g953gzcq](https://wandb.ai/baymaxam/GRID/runs/g953gzcq)，own-best step39500；hybrid Testing为[e4a3b038](https://wandb.ai/baymaxam/GRID/runs/e4a3b038)。Beauty42 NDCG@10为0.04546932，相对Shared的0.03967024提高14.6182%，四指标的Shared−Untied用户配对95%区间均低于零。此结果支持本次选型；它只覆盖一个训练seed和数据集，且同时改变容量、共享约束和梯度耦合，不能单独解释收益原因。来源与完整统计见[测试及配对核验回执](evidence/copmrec-untied-residual-test-20261019/README.md)和[正式结果](../../research/docs/copmrec-v2-untied-residual-results-20261019.md)。

Untied与Shared九格分别保留真实来源，完整主矩阵结果见[最终回执](evidence/bars-untied-m2-final-20261019/README.md)。Beauty42的[机制三组](bars-untied-mechanism-results-20261019.md)也已完成，其中Untied去直接目录CE为独立重训；原Shared loss消融、固定alpha对照与诊断继续保留各自身份。上段单格配对区间仍仅描述Beauty42；多seed效果使用各数据集实际三seed汇总。当前预算和后续执行仍以[当前计划](../../research/ideas/current-plan.md)为准。

## 现有可执行入口

**当前代码的默认入口仍运行Shared；Untied必须显式指定 `--variant untied_residual`。** 模型类、`formal_release.variant`、协议与 checkpoint 恢复校验保持原值。2026-10-20 的命名统一只将 W&B run 显示名及 group 中的 `copmrec` 替换为 `bars`，保留原有阶段、数据集、seed 与 variant；Untied 仍保留其真实 `ablation` 身份。

默认 group 分别为 `paper_main_bars_<dataset>`（Shared Full）、`paper_ablation_bars_<dataset>`（含 Untied 的各 variant）与 `paper_mechanism_bars_<dataset>`（原诊断入口）；BARS 专用机制入口已有的 `bars` 命名保持。既有 group 的额外阶段或部署片段同样保留，仅替换方法名。默认 run 显示名使用原任务模板的 `bars` 前缀；`task_name` 仍使用原实现标识，明确传入的 `--group`、`logger.wandb.group` 与 `logger.wandb.name` 可覆盖默认显示值。

现有 run 的 resolved config、summary、tags、notes，以及 Artifact 名称、版本、digest、URI、来源快照和实际启动 argv 均保存原始执行记录；显示改名不代表重训或改变方法。Linear 当前参考启动命令与后续启动默认值同步使用新 group，带日期的历史回执保留当时 argv。完整映射与核验见[命名统一回执](evidence/bars-naming-unification-20261020/README.md)。

训练均按50k日程运行，每500步raw full-catalog dense Validation，按 `val/ndcg@10` 选择各自own-best；训练后不自动Testing。推理严格核验本方法、数据集、seed、变体、完整状态和SHA256，`copmrec-hybrid-deployment-v1`登记部署身份。默认 `inference_deployment_mode=hybrid`，也可显式 `--deployment hybrid`；辅助dense推理使用 `--deployment dense`，保持独立结果身份。

从仓库根目录运行以下Untied示例。变量分别填入冻结的数据目录、对齐的SID/content bundle与该单元自身own-best URI/SHA256；训练双进程，Testing单进程。下列命令仅说明入口，执行前仍需按当前实验计划确认预算与来源。

```bash
CUDA_VISIBLE_DEVICES=0,1 NPROC_PER_NODE=2 bash ./copmrec_ablation_train.sh \
  --variant untied_residual --dataset beauty --seed 42 \
  --devices '[0,1]' --data-dir "$DATA_DIR" \
  --semantic-id-path "$SEMANTIC_ID_PATH" --embedding-path "$EMBEDDING_PATH" \
  --notes "BARS Untied；主方法；50k scratch"

CUDA_VISIBLE_DEVICES=0 NPROC_PER_NODE=1 bash ./copmrec_ablation_inference.sh \
  --variant untied_residual --deployment hybrid --dataset beauty --seed 42 \
  --devices '[0]' --data-dir "$DATA_DIR" \
  --semantic-id-path "$SEMANTIC_ID_PATH" --embedding-path "$EMBEDDING_PATH" \
  --checkpoint "$OWN_BEST_URI" --checkpoint-sha256 "$CHECKPOINT_SHA256" \
  --notes "BARS Untied；自身own-best；hybrid Testing"
```

复现Shared对照时，分别使用 `copmrec_train.sh` / `copmrec_inference.sh`，不传 `--variant`，并传入该Shared单元自身checkpoint。Untied与Shared不能互换checkpoint或删除variant校验。

## 既有对照与机制分析

现有消融入口允许 `no_mixture`、`no_residual`、`no_joint_ce`、`fixed_alpha_one`、`untied_residual` 和新增 `untied_no_joint_ce`。旧前三移除臂与固定端点保留Shared结构：hybrid下 `no_mixture` 删除mixture NLL并冻结alpha=0.5，属于系统消融；旧 `no_joint_ce` 仍为Shared，不能改称Untied。新 `untied_no_joint_ce` 保留双表、SID CE和mixture NLL，唯一移除直接joint catalog CE，具有独立严格恢复身份。旧 `no_residual` 经共同冻结零表与多步优化等价审计后，可保留原身份复用为共同零残差对照，不另造训练。

当前先行计划为[Untied Beauty42机制与贡献验证](bars-untied-mechanism-plan-20261019.md)，多数据集、多seed后移。新根入口 `bars_untied_mechanism.sh --analysis contributions` 通过CPU `Trainer.test`分析冻结预测，0模型forward；`--analysis generation` 严格恢复当前Untied own-best，执行learned／alpha0生成×catalog／合法decoder路径终排2×2，同池含全部cold，production臂必须逐用户复现正式Top10。配置分别为 `bars_untied_contributions`、`bars_untied_mechanism`；实现已验收，正式实验待用户明确启动，完整参数见[待执行命令](evidence/bars-untied-mechanism-20261019/README.md)。

机制入口 `copmrec_diagnosis.sh` 提供 `hits`、`residual`、`prefix`；hits仍使用原Shared Full/no_mixture/no_residual/no_joint_ce四bundle；residual保留Shared checkpoint的dense评分分析身份，prefix保留原训练真实前缀分析身份。原四来源定义保持，不将Untied替换进旧四bundle诊断。Trainer.test单卡、不更新权重。

固定alpha=1一臂的训练 `lwtzxzre` 与dense Testing `2n4nydm6` 使用step47500 own-best，原Shared Full复用BMX-120。协议与边界见[固定alpha=1比较计划](../../research/docs/copmrec-v2-fixed-alpha-one-plan-20261018.md)和[dense Testing审计](evidence/copmrec-fixed-alpha-one-test-20261018/README.md)。

2026-10-18 hybrid部署迁移对应原Shared九格矩阵、Beauty42三臂系统消融、alpha1推理和零forward hits。原始范围与逐格来源见[hybrid迁移计划](../../research/docs/copmrec-hybrid-migration-plan-20261018.md)；对应Linear为[Shared矩阵BMX-168](https://linear.app/baymax104/issue/BMX-168)、[Shared系统消融BMX-169](https://linear.app/baymax104/issue/BMX-169)和[Shared hits分析BMX-183](https://linear.app/baymax104/issue/BMX-183)。角色调整不改变这些任务的历史运行和完成事实。

## 历史与来源

[方法定义](../../research/docs/copmrec-v2-formal-definition-20261009.md)、[共享／独立残差比较计划](../../research/docs/copmrec-v2-untied-residual-plan-20261018.md)、[历史结果](../../research/docs/copmrec-v0-v1-results-archive-20261009.md)、[原运行面迁移核验](evidence/copmrec-v2-consolidation-20261009/README.md)。M2九次Shared训练与九次单卡dense Testing的原完成记录见[dense完成结果](evidence/copmrec-v2-m2-test-20261009/README.md)。带日期的启动／完成回执保留当时的方法角色与事实，本页记录其后用户决定的角色变更。

旧native/history控制、joint-only临时别名、v1评估、预算续训和混合终排入口已退出运行面；共享组件收敛在copmrec包，LIGER原基线行为保留。历史源码和测试逐字备份见[运行源码归档](archive/copmrec-v0-v1-runtime-20261009/README.md)。旧v0/v1定义与指标只在文档保存，不提供旧版可执行入口。

