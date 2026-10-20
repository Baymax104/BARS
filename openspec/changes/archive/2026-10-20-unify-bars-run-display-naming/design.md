## Context

五个 CoPMRec experiment 直接声明旧 group，W&B logger 从 `tiger_train`／`tiger_inference` 继承 `${task_name}/时间戳`。`task_name` 同时参与 Artifact 命名，不能随论文显示名一起修改。根脚本通过 `liger_common.sh` 统一装配配置，未重复硬编码 group。

## Goals / Non-Goals

**Goals:** 将新运行的 W&B name/group 与 BARS 显示统一；保留用户显式覆盖；保证所有模型、variant、训练、checkpoint、产物与协议身份不变。

**Non-Goals:** 不改 Artifact collection/URI、run ID、`task_name`、method/protocol ID、模型类、experiment 名、文件路径、依赖或运行中的队列；不执行模型训练／推理；不重写历史证据。

## Decisions

1. 新增 `bars_train`／`bars_inference` logger 配置，通过 defaults 继承对应 TIGER logger，仅覆盖 `wandb.name` 为 `${run_display_name}/时间戳`。避免改变其他 baseline，也不在 experiment 重复底层 logger 模板或新增 resolver。
2. 五个 experiment 各自声明与原 `task_name` 同构的 `run_display_name`，只把 `copmrec` 前缀改成 `bars`，并装配相应 logger 组件。保留 seed、variant、部署与分析名称。
3. 默认 group 做原位 token 映射：`paper_main_bars_*`、`paper_ablation_bars_*`、`paper_mechanism_bars_*`；Untied 仍保留 `untied_residual` variant，Shared 根默认不变。
4. 根 shell 不修改：使用真实 argv 捕获与 Hydra compose 证明默认配置、两种 group 语法、含空格的显示名以及末尾 override 的优先级均正确。

## Risks / Trade-offs

- [显示名与稳定身份混淆] → 单独声明 `run_display_name`，保持原 `task_name` 与 Artifact writer 配置，记录允许的配置差异。
- [logger defaults package 变化影响其他参数] → 比较修改前后 resolved Hydra 配置，限制变更为 group、logger.group、logger.name 及新增显示名。
- [外部旧记录与未来默认不一致] → 协调任务同步 W&B 可变字段及 Linear 当前命令；完整历史哈希证据保持原状。

## Migration Plan

保存当前配置与根脚本哈希，完成配置修改并通过聚焦测试，再交协调任务统一 Mutagen 同步。回退只恢复五个 experiment 的元信息及 logger 装配，并停止使用两个新组件；无需迁移或重算任何产物。
