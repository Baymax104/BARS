# BARS 工程命名迁移（2026-10-25）

## 当前入口

按用户要求将当前工程名称统一为 `bars`／`BARS`。本次覆盖49个源码、配置、测试和根脚本路径的迁移，不保留旧包或旧 experiment alias。

| 原名称 | 当前名称 |
| --- | --- |
| `src.recommendation.copmrec` | `src.recommendation.bars` |
| `CoPMRec`、`CoPMRecAblation` | `BARS`、`BARSAblation` |
| `CoPMRecDiagnosis` | `BARSDiagnosis` |
| `CoPMRecMechanismDiagnosis`、`CoPMRecContributionDiagnosis` | `BARSMechanismDiagnosis`、`BARSContributionDiagnosis` |
| `JointMixtureCoPMRec` | `JointMixtureBARS` |
| `copmrec_train/inference.sh` | `bars_train/inference.sh` |
| `copmrec_ablation_train/inference.sh` | `bars_ablation_train/inference.sh` |
| `copmrec_diagnosis.sh`、`copmrec_m3_common.sh` | `bars_diagnosis.sh`、`bars_m3_common.sh` |
| 同名 Hydra model/data/callback/trainer/deployment 与 experiment | 对应 `bars*` 组件与入口 |
| `copmrec_version` 内部属性／顶层配置 | `bars_version` |

新运行的 `task_name`、`method`、显示 tag 和由 task 派生的 Artifact 名称使用 bars。当前运行说明见[bars-versions.md](bars-versions.md)。`bars_train.sh` 仍保持原 Shared 配方；当前 Full 使用 `bars_ablation_train.sh --variant untied_fixed_alpha_half_no_mixture`。

## 兼容与历史范围

现有 checkpoint 的 `copmrec_*` 序列化字段、`copmrec-*` 协议 ID、trace／Artifact metadata 的原 schema 字段保留。它们是已有科学数据的身份，不能通过字符串替换伪造为另一协议；内部类名、路径和属性已迁移。变体、seed、损失、hybrid/dense 选点与完整训练状态校验维持严格要求。

已有 Artifact URI、SHA、运行目录和证据文件保持原值；后续从新入口读取旧文件即可。历史结果／归档／证据文档字节保留，旧 `docs/copmrec-versions.md` 为迁移前快照，当前入口链接已指向新指南。OpenSpec 历史 capability ID 与归档保留，活动规格正文中的工程符号同步更新。

本次保留前一轮清理改动，不启动训练、Testing、远端同步或外部记录修改，不创建 Git 提交。

## 验证

- 迁移前保存14种正式／消融变体的CPU小型完整 checkpoint、loss 和 dense/hybrid 输出；迁移后全部 strict 恢复，重新保存的协议元数据及评价输出逐位一致。
- 全部28个 experiment 完成 Hydra compose，89个项目 `_target_` 均可解析；32个根脚本通过 `bash -n`。
- 命名回归检查旧包源码、旧脚本／组件文件和 Python 标识符不再存在；5个旧 experiment 明确无法 compose。
- 162个既有历史文档与证据文件的SHA256不变。当前文档索引作为明确的允许修改项另行更新。
- Ruff、差异空白检查与新旧两份活动变更的 OpenSpec strict 校验通过。
- 最终全库回归：`uv run --no-sync pytest -q`，1571 passed、1 skipped、4项第三方弃用警告，140.99秒。
