# W&B过时run与Artifact清理完成回执

项目：baymaxam/GRID。用户已明确“确认删除”，现已按其确认的不可变清单完成2个run和27个普通Artifact版本删除，并通过新进程、新API实例的独立回读核验。

全量197个run（196 finished、1 running）、386个普通Artifact版本；两个系统管理类型wandb-history/events不在清理范围。候选2个run、27个普通Artifact版本，逻辑大小513,698,194字节（约489.90 MiB）。逻辑大小包括本地引用及后端去重数据，不等于实际释放的计费存储。

## 执行及独立回读

北京时间2026-10-20 02:27:05核验通过。

| 检查 | 结果 |
| --- | --- |
| 删除run | 2/2，按精确run ID查询均返回不存在 |
| 删除普通Artifact版本 | 27/27，按不可变Artifact ID查询均为DELETED或不可访问 |
| 保留run | 195/195可访问；项目run总数197→195，194 finished、1 running |
| 保留普通Artifact版本 | 359/359仍COMMITTED且digest与删除前一致 |
| 额外run或Artifact删除 | 0 |
| 本地实验重资产删除 | 0 |

原同一SDK实例的runs分页迭代器命中删除前缓存；29次删除调用已全部成功，未重复删除。随后使用新进程、新API实例和直接GraphQL精确查询完成独立核验，初始校验错误和纠正过程保留在回执中。

[逐项删除回执](deletion-receipt.json)、[独立回读](post-delete-verification.json)、[最终范围核验](completion-verification.json)。远端持续写入的执行记录保留于`/data3/weizhenyu/projects/GRID/logs/_audit/wandb_cleanup_20261020_ce9f62501d59`。

## 已删除run

| run ID | 用途 | 替代来源 |
| --- | --- | --- |
| `m03ltj2f` | 旧Shared Full残差2×2 dense评分干预 | 当前Untied机制BMX-205／208；原实验对象和干预定义仍按历史记录追溯 |
| `uogkk2m5` | 旧Shared dense四bundle命中分解 | hybrid旧结果及当前Untied A/B贡献分析已另行留存 |

两run均finished；已保存完整config、summary、notes、logged/used Artifacts身份。资格是当前论文/阶段来源闭包无引用、无保留消费者；不依据结果方向删除。

## 已删除Artifact精确版本

| 类型 | 数量 |
| --- | ---: |
| checkpoint | 4 |
| recommendation_output | 7 |
| analysis | 2 |
| liger_candidate_trace | 7 |
| liger_dispersion_trace | 2 |
| code | 5 |

| Artifact版本 | 逻辑字节 | 删除原因 |
| --- | ---: | --- |
| `baymaxam/GRID/cgbs_fixed_loader_mask_ce_beauty_seed42_train-checkpoint-local-reference:v0` | 84,455,269 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/cgbs_fixed_loader_C128_40k_beauty_seed42_train-checkpoint-local-reference:v0` | 84,857,469 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/cgbs_fixed_loader_A_40k_beauty_seed42_train-checkpoint-local-reference:v0` | 84,455,269 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/cgbs_content_representation_fixed_beauty_seed42_10000-checkpoint-local-reference:v0` | 11,666,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_dispersion_max-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_dispersion_mass-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_factorial_base_alpha1-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_mechanism_max_mixture-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_mechanism_legal_generation-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_50k_fixed05_testing-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_50k_test-recommendation-output:v0` | 7,337,141 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/copmrec_v2_beauty_seed42_hits_full_diagnosis-analysis:v0` | 38,065,538 | 旧诊断run产物 |
| `baymaxam/GRID/copmrec_v2_beauty_seed42_residual_full_diagnosis-analysis:v0` | 40,810,901 | 旧诊断run产物 |
| `baymaxam/GRID/liger_beauty_dispersion_max-candidate-trace:v0` | 14,474,349 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_dispersion_mass-candidate-trace:v0` | 14,474,349 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_factorial_base_alpha1-candidate-trace:v0` | 14,474,157 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_mechanism_max_mixture-candidate-trace:v0` | 14,474,285 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_mechanism_legal_generation-candidate-trace:v0` | 14,474,349 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_50k_fixed05_testing-candidate-trace:v0` | 14,474,157 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_50k_test-candidate-trace:v0` | 14,474,157 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_dispersion_max-dispersion-trace:v0` | 7,565,585 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/liger_beauty_dispersion_mass-dispersion-trace:v0` | 7,565,585 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/grid-source-pvau5wcu:v0` | 316,095 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/grid-source-rizj8teo:v0` | 316,095 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/grid-source-1ucqm40x:v0` | 316,095 | 退休开发或已删除run遗留，无消费者 |
| `baymaxam/GRID/grid-source-uogkk2m5:v0` | 314,181 | 旧诊断run产物 |
| `baymaxam/GRID/grid-source-m03ltj2f:v0` | 314,181 | 旧诊断run产物 |

全部27版本均重新按精确ID/digest读取，COMMITTED、无消费者、无Registry/Portfolio链接；文件path/size/digest及可见本地引用索引已备份。精确Artifact ID、aliases与元数据见[lineage_plan.json](lineage_plan.json)。

## 保护范围

保留195个run及其有效来源链：当前Untied主矩阵与三组机制、Shared hybrid对照、仍被DASFAA冻结稿引用的旧结果、外部基线及上游、IntRR已完成和运行中的训练。两个旧前缀诊断2nosdem5/jve5nu3s仍支撑冻结DASFAA概率观测，继续保留；五个看似重复的LETTER旧run仍生产正式使用的预测Artifact，继续保留。

两个技术来源尚未完全确定的手工local-reference checkpoint暂不删除：TIGER beauty v0和LIGER beauty v3，详见清单ambiguous_orphans_held。没有将全部Linear历史issue自动转换为W&B删除对象。

## 确认与执行边界

用户已确认清单SHA，执行前再次核验全部候选精确ID/digest/消费者/Registry链接、27份保护来源文件SHA以及运行状态。实际逐版本删除27次，再以delete_artifacts=False分别删除两个run，防止隐式扩大范围；共29次删除调用，无重复调用。项目、系统管理history/events及node1本地checkpoint、日志和证据均未作为删除目标。

清单SHA256：`ce9f62501d595d31b1eca653754c3571af1850c52f877a59425c42bb7c6ed457`。

用户确认已记录在[authorization.json](authorization.json)，批准范围严格为本清单2个run和27个Artifact版本。

[全量run盘点](inventory_runs.json)、[普通Artifact版本与生产/消费图](inventory_artifacts.json)、[精确删除清单](deletion-plan.json)、[删除前完整元数据和文件索引](lineage_plan.json)、[删除前核验](verification.json)。
