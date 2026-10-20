## ADDED Requirements

### Requirement: TIGER通用协议一致

系统 MUST 将IntRR除模型内部参数外的运行配置对齐当前TIGER，包括数据/SID、采样、历史信息、batch、workers、优化器、scheduler、训练步数、验证选点及评价输出语义。

#### Scenario: 轻量compose比较
- **WHEN** 以相同输入compose IntRR及TIGER train/inference配置
- **THEN** 通用参数深比较一致，差异仅为IntRR身份与模型/必要数据表示适配

### Requirement: 统一脚本入口

系统 SHALL 提供train/inference根脚本，经统一src.main运行，支持两种notes、显式dry-run及末尾Hydra override。

#### Scenario: quoting和覆盖
- **WHEN** notes/路径含空格、引号或等号，且附额外Hydra override
- **THEN** 参数无shell执行副作用地传递，额外override优先，默认不启用dry-run

#### Scenario: 错误输入
- **WHEN** 必填值为空、seed/process/port非法或推理未给checkpoint
- **THEN** 脚本明确失败，不启动任务

### Requirement: 有界验证及清理

系统 MUST 将node1验证限制于dry-run及最多5step训练和有限预测，关闭外部发布；完成后删除本次临时运行记录并保留正式代码和提案。

#### Scenario: 实际集成检查
- **WHEN** Mutagen三会话同步完成并执行5step检查
- **THEN** 核对实际5step及有限loss、checkpoint恢复和预测，所有本次临时日志/checkpoint/输出/tmux及源码审计文件清理后确认不存在
