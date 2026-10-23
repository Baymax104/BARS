# W&B ablation 过时记录清理

日期：2026-10-23。用户明确要求清理 W&B ablation 组中过时的 run 和 Artifact。项目 `baymaxam/GRID`，范围仅 `ablation`／`ablation_main`；实际命中22条run，均在 `ablation_main`。**已删除14条过时run与24个普通Artifact版本，组内剩余8条有效run；7个系统history版本被服务拒绝独立删除且在run删除后仍存在。** 状态为 `completed_with_service_managed_retention`，最终回读时间2026-10-23 14:04:32北京时间，见 [verification.json](verification.json)。

最终16项检查通过：14条目标run在整个项目中均不存在；24个普通Artifact版本已删除；8条保留run的配置、summary、状态及输出集合保持；24个需要保留的Artifact版本身份与完整manifest保持。原清单31个Artifact目标未全部删除，7个系统history保留情况单独列入验证文件，不计入24个成功删除版本。

## 冻结范围

[原始盘点](inventory-before.json)保存22条run的配置、summary、notes、文件清单、输入输出Artifact，以及55个输出版本的manifest、生产者和消费者。[清理清单](plan.json)最初冻结14条旧run和31个独占Artifact目标，另保留8条当前有效run及24个Artifact版本。执行使用清单SHA256校验，并在删除前重新读取状态和依赖；原清单保持不变，服务限制与实际执行差异记录于最终回执。

| 删除的旧条件 | Training | Testing |
| --- | --- | --- |
| 原Shared去Catalog CE | `izwmwyig` | `fx6s5o4u` |
| 原Shared去mixture | `qhzzhnxp` | `3yubqzcr` |
| 原Shared零残差 | `gtwv2c4n` | `xzfp1pgt` |
| 原Shared固定alpha1 | `lwtzxzre` | `92gwx86m` |
| 临时Untied固定alpha1探索 | `860tn67l` | `fs5fgu76` |
| 临时Untied固定alpha0.5三损失探索 | `shwmvcol` | `ybhdif6a` |
| 临时Untied近零初始化学习alpha探索 | `oqw8o4t7` | `na7kdgh2` |

原31个Artifact目标由6个checkpoint、4个推荐预测、14个源码快照、7个训练history组成。其中24个普通版本按具体版本删除；7个history为系统管理版本，服务端拒绝独立删除，所属run删除后仍存在，见[服务端回执](service-history-delete-rejection.json)及最终验证中的逐版本记录。未尝试绕过服务限制。run调用 `delete_artifacts=False`，避免级联删除需要保留的独立Artifact。

| 保留的有效条件 | Training | Testing |
| --- | --- | --- |
| 当前M3 Shared | `gu3l2s2s` | `e0m3cdsi` |
| 当前M3双侧零残差 | `1k2ebqaw` | `1ipsthvi` |
| 当前M3去Catalog CE，1/0/0 | `7u93dubs` | `srta7ooi` |
| 当前论文仍引用的Shared主对照 | `rmgfscr0` | `64mjlgze` |

Shared主对照保留依据为 `research/src/data/experiment-evidence.json` 中当前有效来源；三个新臂依据为已独立验收的[当前M3结果](../../bars-current-method-m3-results-20261023.md)。Full、M2及机制组不属于本次run删除范围。

以下4个旧Artifact被组外run引用，保留不可变版本：

- `copmrec_v2_beauty_seed42_no_mixture_train-checkpoint:v0`：`jve5nu3s`。
- `copmrec_v2_beauty_seed42_no_mixture_hybrid_inference-recommendation-output:v0`：`ppjhagjq`。
- `copmrec_v2_beauty_seed42_no_joint_ce_hybrid_inference-recommendation-output:v0`：`ppjhagjq`。
- `copmrec_v2_beauty_seed42_no_residual_hybrid_inference-recommendation-output:v0`：`3e62b44e`／`84a07f71`／`ppjhagjq`。

上述旧生产run仍按清单删除，因此历史run URI后续可能不可解析；独立Artifact版本及本地盘点保留生产身份。历史记录不改标为新方法结果，也不自动改写组外历史分析。

## 备份与验证

[备份验收](backup-verification.json)核验21个小体积源码／训练history版本，共5,188,388 bytes，保存在 `artifact-backup/`，每个文件匹配原manifest的MD5并另存SHA256。[node1文件核验](node1-file-verification.json)确认6个checkpoint和4个预测文件仍存在，大小与MD5均匹配原manifest；未删除或修改node1文件。

W&B SDK对history的 `digest` 在加载manifest前后可能返回不同值；本次统一加载manifest后比较完整摘要，并核对不可变Artifact ID和每个manifest条目的摘要、大小与引用。该处理不放宽内容一致性要求。

实际逐项删除及时间见 [deletion-receipt.json](deletion-receipt.json)。最终回读验证目标run在项目中消失、24个普通Artifact版本消失，以及8条保留run的配置／summary／输出集合和24个保留Artifact的身份／完整manifest均保持；7个系统history版本的身份与完整manifest也单独核验并标记为服务端保留。脚本 [cleanup.py](cleanup.py)只执行服务管理、备份与文件校验，不运行训练或模型forward。

本地历史文档、原实验账本和node1重资产保留。Artifact的逻辑大小包含 `file://` 引用，不据此声称释放了相同大小的W&B存储。
