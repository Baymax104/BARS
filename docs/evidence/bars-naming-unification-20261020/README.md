# BARS run 显示名与分组统一回执

日期：2026-10-20。按用户授权完成 W&B 既有 run、Linear 当前复现命令与后续启动默认值的统一；全量回读及独立核验均通过。

## 完成范围

| 对象 | 执行与验证结果 |
| --- | --- |
| W&B `baymaxam/GRID` | 盘点全部 195 个 run；更新其中 60 个已完成 run 的显示名及 group，覆盖 12 对分组映射；fresh API 全量回读与独立 connector 查询的旧显示名称／分组残留均为 0 |
| Linear | 全量核对 146 个 issue、6 个 milestone、4 份文档、项目及评论；修改 16 个 issue 和 1 份 M3 协议文档中的 40 条当前复现命令；旧 group 残留为 0，40 条原始实际命令逐字保留在历史折叠块 |
| 后续启动 | 修改 5 个 experiment，新增 2 个轻量 logger；将显示名与稳定 `task_name` 分离；27 组真实脚本参数与 resolved Hydra 对比通过，显式 group/name 及末尾 override 仍有效 |
| node1 | 按项目入口执行 Mutagen flush；3 个会话均为 Watching for changes，7 个目标配置的本地／远端 SHA256 相同 |
| Artifact | 既有 359 个普通 Artifact 的身份、版本、digest、metadata、alias 及来源关系保持；本轮未进行 Artifact 写入。期间并行 IntRR 任务新增 1 个 checkpoint，单独记录，不计为本轮改名产物 |

## 统一规则

只在 W&B run 显示名和 group 中将 `copmrec` 替换为 `bars`。原有阶段、variant、dataset、seed、hybrid 等额外片段及时间后缀全部保留。例如：

| 原显示值 | 当前显示值 |
| --- | --- |
| `copmrec_v2_beauty_seed42_train/<timestamp>` | `bars_v2_beauty_seed42_train/<timestamp>` |
| `paper_main_copmrec_beauty` | `paper_main_bars_beauty` |
| `paper_ablation_copmrec_beauty` | `paper_ablation_bars_beauty` |
| `paper_mechanism_copmrec_hybrid_beauty` | `paper_mechanism_bars_hybrid_beauty` |

未来入口默认 group 为 `paper_main_bars_<dataset>`、`paper_ablation_bars_<dataset>` 与 `paper_mechanism_bars_<dataset>`。Shared／Untied 现有运行身份、variant 与 phase 不因显示改名而调整；默认 Shared 入口保持原行为，Untied 仍需显式 variant。

## 来源与历史边界

W&B mutation 仅提交 `id`、`displayName`、`groupName`，通过全局 storage ID 精确定位。逐项对比确认 run ID、storage ID、URL、config、summary、notes、tags、jobType 和完成状态不变。原 config 中的旧 group 继续表示执行时配置；服务端当前 group 为更新后的显示元数据。没有调用会额外写入 config／summary 的 `Run.update()`。

`task_name`、模型／脚本／experiment 标识、研究协议、Artifact 名称／版本／digest／URI、checkpoint 与输出路径保持原身份。Linear 页面的新模板仅更新 group；实际命令的原文保存在相邻历史折叠块。模板保留原 run ID／输出目录供追溯，实际重新执行须按原说明使用新 ID／目录及相应 dense／hits override。

本轮未启动或重跑训练、Testing、诊断，未修改 Linear 状态、里程碑、标题、父子关系或实验预算，未创建 Git commit。项目名称及历史来源中的 CoPMRec 标识继续用于追溯。

## 证据与验证

- [W&B 改名前快照及可逆映射](wandb/naming-mapping.json)、[逐项 mutation 回执](wandb/mutation-receipt.jsonl)、[fresh API 回读](wandb/verification.json)、[独立 connector 计数](wandb/connector-verification.json)。
- [Artifact 前快照](wandb/artifacts-before.json)、[后快照](wandb/artifacts-after.json)、[完整对比](wandb/artifact-verification.json)。
- [Linear 完整审计与执行回执](linear/README.md)、[最终全量核验](linear/final-verification.json)、[改名前快照](linear/before-full.json)、[精确补丁与原命令](linear/proposed-patches.json)。
- [跨 W&B／Linear 分组对照](cross-surface-verification.json)：40 条当前命令均精确对应 live W&B 新 group，命令其余字符不变。
- [本地实现与验证](local-launch-implementation.md)、[配置差异](local-launch-config.patch)、[27 组配置对比](local-launch-verification.json)、[聚焦测试](local-launch-tests.json)：147 passed，4 个依赖弃用警告；8 个 shell 语法检查通过，OpenSpec 严格校验通过。
- [同步与 node1 文件哈希](sync-verification.json)、[独立一致性审计](consistency-audit.md)、[research 状态边界验证](research-naming-verification.json)。
- [最终汇总与证据哈希](completion-verification.json)。

所有真实外部修改均可按 storage ID 或精确正文补丁追溯；W&B 原值保存在映射中，Linear 原始正文可无损恢复。历史来源文件、论文数据和 hash 绑定的构建产物没有批量替换。
