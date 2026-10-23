# W&B history 组清理

日期：2026-10-23，北京时间。用户明确要求：核对history组有无用途，无用则run和Artifact一起清理。项目 `baymaxam/GRID`，范围为精确group `history`，原有2条finished run。**现已删除两条旧run与4个普通Artifact版本，history组剩余run为0。** 最终回读时间14:28:19，状态 `completed_with_service_managed_history_retention`，见[独立验证](verification.json)。7项检查全部通过；1个系统history版本仍存在且已备份，未计入删除数量。

## 用途判断与范围

两条run分别为旧Untied训练 `g953gzcq` 和推荐测试 `e4a3b038`，variant `untied_residual`、`alpha_policy=learned`，属于原 `copmrec-v2-ablation-20261009-v1`。它们已被当前fixed alpha0.5、无mixture loss、hybrid Validation选点来源替代；当前Full为 `httwyhka → prt5r0v5`。

当前 `research/src/data/experiment-evidence.json` 与当前M3结果均未引用这两条旧run；`research/ideas/current-plan.md` 的相关文字位于“以下为旧主版本执行与写作记录”之下，仅保留原时点事实。实时Artifact lineage显示无组外消费者，旧checkpoint仅由待删的旧Testing使用。因此这两条run不再承担当前论文或实验依赖，只具有历史追溯价值。

来源见[原始查询](query-before.json)、[完整盘点](inventory-before.json)和[冻结清单](plan.json)。清理4个普通Artifact版本：

- `copmrec_v2_beauty_seed42_untied_residual_train-checkpoint:v0`。
- `copmrec_v2_beauty_seed42_untied_residual_hybrid_inference-recommendation-output:v0`。
- `grid-source-g953gzcq:v0`。
- `grid-source-e4a3b038:v0`。

系统管理 `run-g953gzcq-history:v0` 按W&B已经验证的服务限制单独记录，不尝试独立删除，不计入4个普通版本的删除数量。run使用 `delete_artifacts=False`，所有普通Artifact按具体版本处理。

## 备份和验证

[备份验收](backup-verification.json)确认3个源码／训练history版本共743,194 bytes保存至 `artifact-backup/`，文件MD5与原manifest一致并另存SHA256。[node1文件验证](node1-file-verification.json)核验旧checkpoint与预测文件的实际大小／MD5一致，未修改或删除远端文件。

执行脚本[cleanup.py](cleanup.py)复用已验收的mechanism审计工具，动态限定group、run ID和本轮文件目录；冻结计划SHA256检查及消费者复核通过后才删除。实际逐项操作与时间见[删除回执](deletion-receipt.json)。

最终回读已确认history组为空、两条旧run在整个项目中不存在、4个普通Artifact版本均不存在，13条保留来源（8条ablation、3条mechanism和当前Full训练／Testing）仍finished。系统 `run-g953gzcq-history:v0` 单独核验为服务端保留，身份与完整manifest保持。原研究历史、预算与前两轮清理回执保持其历史时点含义；本次不创建run、不执行模型forward、不修改论文或Linear。
