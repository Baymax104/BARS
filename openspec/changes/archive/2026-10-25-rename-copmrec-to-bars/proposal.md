## Why

论文与显示名已经使用 BARS，当前源码、Hydra 和根脚本仍混用 CoPMRec，增加查找与运行成本。按用户要求统一工程名称，同时保持历史科学来源与模型兼容。

## What Changes

- **BREAKING** `src.recommendation.copmrec` 迁移至 `src.recommendation.bars`，`CoPMRec*`／`JointMixtureCoPMRec` 改为 `BARS*`／`JointMixtureBARS`。
- **BREAKING** 当前 `copmrec*.sh`、同名 Hydra 组件与 experiment、测试文件／fixture／helper 改为 `bars*`，新 task/artifact 名使用 bars。
- 保持已序列化 checkpoint 字段、协议 ID、已有 URI／SHA 原值；不提供旧工程入口的 alias。
- 当前 README、方法指南与活动规格中的代码入口同步更新；历史结果、归档、证据文件和历史规格 ID 保持原身份。

## Capabilities

### New Capabilities

- `bars-engineering-naming`: 统一 BARS 工程入口与冻结协议的兼容边界。

### Modified Capabilities

无算法或科学协议要求变更；当前规格中的路径与类名引用同步工程迁移。

## Impact

src、configs、根脚本、tests、AGENTS.md、README、当前运行指南和活动 OpenSpec 文本。保留上一轮未提交清理，不启动实验，不修改远端环境、历史产物、相邻 research 仓库或 Git 历史。
