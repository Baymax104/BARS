# bars-run-display-naming Specification

## Purpose
统一 BARS 的 W&B 显示名与默认 group，同时保留原入口、执行协议、checkpoint 和 Artifact 身份。
## Requirements
### Requirement: BARS 显示名与稳定任务身份分离

系统 SHALL 为现有 CoPMRec 训练、推理、消融和诊断 experiment 提供独立 `run_display_name`，通过 BARS logger 组件生成 `bars_*` 的 W&B name。既有 `task_name`、model/class、experiment、variant、protocol、Artifact 名称／引用及路径 MUST 保持原值。

#### Scenario: 运行默认 Shared 和 Untied 配置

- **WHEN** 用户通过根脚本装配默认 Shared 或 `untied_residual` 的训练／推理
- **THEN** W&B 显示名称使用 `bars` 前缀并保留数据集、seed、variant 与阶段，稳定 `task_name` 仍使用既有 `copmrec` 身份，模型和 Artifact writer 的身份保持不变

### Requirement: 分组与用户覆盖一致

五个现有 experiment 的默认 group SHALL 原位使用 `paper_main_bars_*`、`paper_ablation_bars_*` 或 `paper_mechanism_bars_*`。系统 MUST 保留根脚本的 `--group` 两种语法、额外 Hydra override 以及显式 `logger.wandb.name` 覆盖能力，并按现有优先级应用。

#### Scenario: 默认分组

- **WHEN** 用户不指定 group 装配训练、推理或诊断
- **THEN** resolved group 和 logger group 使用对应的 BARS 默认分组，不改变实验阶段或 variant

#### Scenario: 显式显示元信息覆盖

- **WHEN** 用户指定含空格的 group 或 name 并追加 Hydra override
- **THEN** 参数经根脚本完整透传，末尾 override 按现有优先级生效，空 group 仍被拒绝，模型和产物身份不受显示覆盖影响

### Requirement: 变更边界验证

本次修改 SHALL 仅影响 W&B 显示元信息和必要 logger 装配，不改共享 TIGER logger、runtime、根脚本实现、既有数据或运行中的任务。验证 MUST 使用轻量 compose、shell 语法检查与现有针对性测试，不运行完整 experiment。

#### Scenario: 验证命名迁移

- **WHEN** 对修改前后同一真实根脚本 argv 做配置比较
- **THEN** 除 group、logger group/name 与新增显示名外的 resolved 配置一致，根 shell 和 src 哈希保持不变
