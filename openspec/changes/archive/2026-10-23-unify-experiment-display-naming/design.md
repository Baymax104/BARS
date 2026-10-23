## Context

当前 BARS 使用 `paper_*_bars_<dataset>`；其他方法常直接使用方法名。TIGER 与诊断脚本的旧 `--group` 选择 quantizer；IntRR 已将此选择保存在 `sid_type`，另用 `--wandb-group` 控制显示分组。

## Goals / Non-Goals

**Goals:** 默认显示组遵守用户规则，组内名称保留方法、数据集、seed、阶段及可辨识变体；保持旧脚本 tokenizer 参数可用。

**Non-Goals:** 不修改训练、预测、checkpoint/deployment contract、`task_name`、Artifact 名称、既有 raw evidence 和论文；不启动训练、测试或同步。

## Decisions

- 新增/复用 `run_display_name`；logger 用它显示名称，`task_name` 继续负责内部身份和产物名。
- 数据集只在缺少显式 `dataset_name` 的入口中通过 `display_dataset_name` 取可选旧 metadata；无 metadata 时由 `data_dir` 最后一个路径片段生成，同时接受 Windows 和 POSIX 分隔符。不占用原可选的 `dataset_name` 键，保留旧 `+dataset_name=...` 命令。
- TIGER/旧诊断脚本将 `--group` 的 quantizer 写入独立 `sid_type`，实际 group 使用配置默认值；`--wandb-group` 与尾随 Hydra override 仍可覆盖显示组。
- BARS `untied_residual` 入口虽保留历史 ablation 配置/契约，显示分类为主方法；Shared 根入口和其余变体显示分类为消融。alpha 探索名称保留具体固定值/初值。

## Risks / Trade-offs

- 旧命令显式覆盖 group 可继续指定旧组 → 本次同步更新 Linear 命令，仓库默认与新规则一致。
- 显示名称变化可能误改产物身份 → compose 验证 `task_name` 与 writer identity，并保留原契约不变。
- Shared/Untied 名称可能混淆 → 明确共享形式；临时探索加 `alpha_exploration` 标识。
