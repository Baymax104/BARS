## Context

依赖已完成的RAN核心及推荐接入提案。当前不同baseline的外部配置并非完全相同，用户已明确选择以TIGER为参照。本模块以现有可执行配置为准，不使用作者YAML的外部训练设置。

## Goals / Non-Goals

目标：通过统一 `src.main` 提供IntRR训练/推理，自动验证通用协议一致，并完成临时有界集成检查。非目标：正式训练、结果比较、依赖环境变更或DECOR接入。

## Decisions

- data配置继承 `tiger_train` / `tiger_inference`，仅新增catalog及替换为压缩wrapper的collate；原预处理和dataloader参数原样继承。
- experiment直接使用TIGER trainer、callbacks和logger；IntRR独立任务名、来源commit与baseline_protocol标记。SID类型通过 `sid_type` 结构化记录，W&B group默认intrr并支持override。
- model保持独立root，optimizer/loss配置与metrics复制TIGER对应子树并深比较，避免把TIGER encoder/decoder等无用装配带入IntRR。模型内部参数清楚列出，alignment默认0.1，公开代码YAML差异在SOURCE记录。
- 根脚本共享小型parser，选项对齐TIGER，字符串使用Hydra quoting，默认不dry-run，用户Hydra overrides放最后。单卡同样经 `uv run torchrun ... -m src.main`。
- node1仅用现有环境与数据，Mutagen resume/flush/status三会话通过后执行。dry-run1步无发布；5step集成显式关闭W&B发布，可临时覆盖worker/验证频率以完成有界检查，正式默认配置保持不变。
- 5step结束核对实际step、finite loss、own checkpoint恢复和有限预测输出。所有临时产物放唯一任务目录，校验绝对路径后删除并确认不存在；不清理任何已有运行。

## Risks / Trade-offs

外部配置漂移 → 以compose后的深比较测试锁定TIGER。作者默认外部协议不同 → 文档标注本实现为TIGER统一协议比较基线。GPU占用 → 先检查node1空余，仅运行有界验证。临时W&B记录难清理 → 验证禁用外部logger及发布callback，从源头不创建。
