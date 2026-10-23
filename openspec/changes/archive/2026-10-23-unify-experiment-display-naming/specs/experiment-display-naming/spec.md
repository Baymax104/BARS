## ADDED Requirements

### Requirement: 按研究角色统一显示分组

系统 SHALL 将同一方法的多数据集、多 seed 主实验归入 `{method}_main`，机制实验归入 `mechanism_main`，消融实验归入 `ablation_main`。BARS Untied 为主版本，Shared 与临时 alpha 探索作为消融分类。

#### Scenario: 同方法不同数据集

- **WHEN** LIGER 运行不同数据集或 seed
- **THEN** 默认 W&B group 均为 `liger_main`

#### Scenario: BARS 的残差版本和临时探索

- **WHEN** 选择 Untied 主版本、Shared 根入口或临时 alpha 变体
- **THEN** 分别归入 `bars_main`、`ablation_main` 和 `ablation_main`

### Requirement: 显示名称完整且不改变内部身份

系统 SHALL 让组内名称区分方法、数据集、seed、变体和阶段，并保留时间戳。系统 MUST 保留 `task_name`、模型和协议、checkpoint/deployment contract 及 Artifact 身份。

#### Scenario: BARS Shared 预测

- **WHEN** 使用 Shared 根入口生成预测
- **THEN** 显示名称包含 `bars`、数据集、seed、`shared`、部署方式和 `test`，原内部 task 与产物名不变

### Requirement: 分离 tokenizer 选择和显示组覆盖

脚本 SHALL 保留旧 `--group` 的 tokenizer 选择能力，以 `sid_type` 传入配置，显示组使用角色对应默认值。脚本 MUST 保留后续 Hydra override 的覆盖能力和引号内容。

#### Scenario: TIGER 选择 RVQ

- **WHEN** TIGER 脚本收到 `--group rvq`
- **THEN** 解析后的 `sid_type` 为 `rvq`，默认显示组为 `tiger_main`，名称保留 `rvq`

#### Scenario: 用户覆盖显示组

- **WHEN** 同一命令带显示分组参数和尾随 `group="custom group"`
- **THEN** 最后 override 生效且空格、引号不丢失

#### Scenario: 旧命令附加数据集 metadata

- **WHEN** 原本没有 `dataset_name` 默认值的入口收到旧 `+dataset_name=home_and_kitchen`
- **THEN** 配置继续成功装配，显示名称优先使用该 metadata，原 `data_dir` 保持不变
