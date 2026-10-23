# W&B mechanism 过时记录连带清理

日期：2026-10-23，北京时间。用户在ablation清理后明确要求连带清理mechanism中过时run和Artifact。项目 `baymaxam/GRID`，范围 `mechanism`／`mechanism_main`，实际11条run均在 `mechanism_main`。**已删除8条旧run和20个普通Artifact版本，机制组剩余3条有效run；此前4个旧ablation版本也已全部删除。** 最终回读时间14:12:53，状态 `completed_with_service_managed_history_retention`，见[独立验证](verification.json)。

最终10项检查全部通过：8条旧run在整个项目中不存在，20个普通版本不存在；3条保留run配置、summary、状态和输出集合保持，7个保留Artifact的ID／digest／完整manifest／alias保持；此前8条ablation run继续存在。系统管理 `run-ec98cca4-history:v0` 仍存在且内容一致，已单独备份和登记，不计入20个成功删除版本。

## 冻结清单

[原始查询](query-before.json)、[完整盘点](inventory-before.json)与[冻结计划](plan.json)记录11条run、28个Artifact版本及配置、summary、notes、输入输出和完整manifest。删除目标为8条旧run、20个普通Artifact版本；另有1个系统管理history版本，按已验证的W&B服务限制单独保留并记录，不重复尝试独立删除。

| 删除的旧run | 原分析或实验 |
| --- | --- |
| `2nosdem5` | 旧Shared Full前缀诊断 |
| `jve5nu3s` | 旧Shared no_mixture前缀诊断 |
| `ppjhagjq` | 旧Shared四bundle命中与排名分解 |
| `84a07f71` | 2026-10-19旧Untied A组贡献分析 |
| `ec98cca4` | 旧Untied去Catalog CE训练，原三损失体系中的1/0/1 |
| `0474e89a` | 上述旧去Catalog CE模型Testing |
| `1241f8aa` | 2026-10-19旧Untied生成×排序分析 |
| `3e62b44e` | 2026-10-19旧Untied B组贡献分析 |

普通Artifact目标包括6个analysis、2个checkpoint、4个推荐预测、8个源码快照；只删除明确版本，不删除整个collection。旧贡献 `bars_untied_beauty_seed42_contributions-analysis:v0/v1` 和旧生成排序 `bars_untied_beauty_seed42_generation_ranking-analysis:v0` 均属于删除目标；当前对应v2与v1保留。

此前因这批历史机制消费者而保留的4个ablation版本，本次均纳入：

- `copmrec_v2_beauty_seed42_no_mixture_train-checkpoint:v0`。
- `copmrec_v2_beauty_seed42_no_mixture_hybrid_inference-recommendation-output:v0`。
- `copmrec_v2_beauty_seed42_no_joint_ce_hybrid_inference-recommendation-output:v0`。
- `copmrec_v2_beauty_seed42_no_residual_hybrid_inference-recommendation-output:v0`。

## 保留来源

保留3条run、7个输出Artifact版本，并验证配置、summary、状态、输出集合、Artifact身份、完整manifest及alias：

- `gkwknl0l`：当前fixed alpha0.5、两损失M3生成×排序，analysis版本v1。
- `6cpl285w`：当前M3冻结预测贡献，analysis版本v2。
- `lu8oct42`：LIGER同一checkpoint、无历史排除dense辅助对照。保留依据为当前研究状态的 `active_research_scope.additional_internal_control`，以及既有来源记录 `internal_beauty42_dense_no_history_run`；不因日期较早删除有效辅助对照。

上一轮保留的8条ablation run也需继续保持。Full、M2、其他基线组与Linear不在本次修改范围。

## 备份与执行

[备份验收](backup-verification.json)确认9个源码／训练history版本共2,781,993 bytes保存至 `artifact-backup/`，每个文件的MD5匹配原manifest，另记录SHA256。[node1文件验证](node1-file-verification.json)核验61个文件引用的实际字节、大小与MD5一致，包括旧分析JSON／CSV／预测及checkpoint；未修改或删除node1资产。

执行前重新核对每个待删版本的ID、加载manifest后的digest、逐文件内容及消费者。所有删除均按冻结计划；run使用 `delete_artifacts=False`，保留范围外引用与当前版本。实际时间与逐项操作见[删除回执](deletion-receipt.json)。

服务端保留的系统history为 `run-ec98cca4-history:v0`；W&B此前已返回 `cannot delete system managed artifact`，本轮不再调用独立删除。所属run删除后已单独回读确认该版本仍存在、身份与完整manifest一致，不将它计入20个普通版本的成功删除数量。加上此前ablation轮保留的7个，此两轮共有8个系统history版本未删除。

历史完成事实、账本和原ablation清理证据不重写；新的删除意味着旧run URI后续可能不再解析。本次仅存储清理，训练、Testing、新run和模型forward均0。源码和checkpoint的本地／node1副本保留，逻辑Artifact大小不等于实际W&B存储释放量。
