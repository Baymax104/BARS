## Why

现有 W&B 分组按数据集、日期和旧方法名分散，组内名称又缺少 seed 或阶段，难以横向比较。用户要求将同方法主实验归入 `{method}_main`，机制和消融分别归入 `mechanism_main`、`ablation_main`。

## What Changes

- 统一未来运行的默认 group 和 display name；名称包含方法、数据集、seed、变体和阶段。
- 保留 `task_name`、模型/协议、checkpoint 和 Artifact 身份；BARS 显示名使用 `bars`。
- Untied 主版本使用 `bars_main`；Shared 根入口明确归为消融，临时 alpha 探索也归入消融。
- 保留脚本 tokenizer 参数与额外 Hydra override 的兼容性，并区分显示分组。

## Capabilities

### New Capabilities

- `experiment-display-naming`: 实验显示分组和组内名称规则。

### Modified Capabilities

无。

## Impact

涉及 experiment/logger 配置、根目录 launcher 的分组默认值、Hydra 显示名称 resolver 和聚焦测试。无新增依赖，不执行实验或历史产物迁移。
