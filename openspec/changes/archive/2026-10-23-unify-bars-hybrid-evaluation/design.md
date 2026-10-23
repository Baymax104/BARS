## Context

W&B有77条BARS记录，其中17条为独立dense测试、28条名称含hybrid。训练配置同样可能保存prediction_mode=dense，故不能仅以该字段删除训练run。

## Goals / Non-Goals

Goals：删除已明确授权的dense测试记录，默认hybrid，推荐测试名称仅保留test/validation阶段，并同步当前记录。

Non-Goals：不删除训练、checkpoint、上游或Artifact，不修改其他方法，不改变训练选点和内部机制分析，不启动实验。

## Decisions

- 删除范围同时要求BARS身份、prediction_mode=dense、独立evaluation_split和真实test指标；不删除复合机制分析run。
- 使用Run.delete(delete_artifacts=False)，先保存配置/指标/Artifact版本和依赖快照，再验证独立Artifact保留。
- 存活记录只改显示名称，去掉_hybrid_；原始配置、task_name和产物身份保留历史执行事实。
- 公共BARS推理脚本只接受hybrid作为兼容参数；无需提供部署选择。旧dense脚本参数明确拒绝，其他Hydra override继续透传。
- 训练dense验证和内部诊断能力继续承担原职责，不生成新的对外dense测试记录。

## Risks / Trade-offs

- 删除run会使旧run页面和run型URI不可访问 → 本地运行快照和独立Artifact版本保留，Linear将删除记录标为历史，当前入口不再引用。
- 旧脚本/历史命令包含dense参数 → 历史正文保留原义，当前命令改用唯一默认入口。
