## Why

论文名称已统一为 BARS，但当前实验入口仍会生成 CoPMRec 的 W&B 显示名称与分组，导致 W&B、Linear 启动命令和未来运行不一致。本次统一可变显示元信息，同时保留产物和实验协议的既有身份。

## What Changes

- 为 BARS 训练和推理新增轻量 logger 组件，复用既有 W&B 组件，仅将显示名称与稳定的 `task_name` 分离。
- 五个现有 CoPMRec experiment 的默认 group 使用 `paper_*_bars_*`；显示名称仅将原任务模板中的 `copmrec` 前缀改为 `bars`。
- 根脚本继续通过统一入口装配 Hydra，保持显式 group/name 与末尾 override 的优先级；Shared 和 Untied 的 variant、训练和部署保持原定义。
- 更新当前命名政策并记录针对性验证。外部 W&B/Linear 的修改由同一用户授权的协调任务负责；历史执行证据不改写。

## Capabilities

### New Capabilities

- `bars-run-display-naming`：独立管理 BARS 的 W&B 显示名称与分组，并保护稳定实验及产物身份。

### Modified Capabilities

无。模型、协议、输出 bundle 和 Artifact 语义保持不变。

## Impact

新增两个 `configs/logger/` 组件；修改五个 `configs/experiment/copmrec*.yaml` 的显示元信息和 logger 装配；扩展既有配置／脚本测试并更新当前版本说明。不修改 runtime 代码、依赖、根脚本实现、历史证据、既有 checkpoint 或运行中队列。
