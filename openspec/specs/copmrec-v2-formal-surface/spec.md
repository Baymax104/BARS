# copmrec-v2-formal-surface Specification

## Purpose
将 CoPMRec 活动运行面收敛为正式 v2，统一默认训练推理、三臂消融和固定产物诊断，约束计划登记、实际完成核验及授权后的历史清理，保护保留实验所依赖的来源和产物。
## Requirements
### Requirement: 单一正式运行面

系统 SHALL 使用 CoPMRec v2 默认训练、dense 验证与 hybrid 推理；三目标为 SID CE、joint catalog CE、mixture NLL，所有阶段无历史排除；旧 native view 和迭代入口 SHALL 归档移出运行面。显式 dense 辅助推理 SHALL 保留以复现旧 dense 评分证据；hits 主部署分析 SHALL 使用同一 hybrid 协议的四份产物，原 residual 全目录分析 SHALL 保留 dense 身份。

#### Scenario: 默认入口

- **WHEN** 用户 compose copmrec_train 或 copmrec_inference
- **THEN** 获得 v2 模型与准确的无排除配置；训练双卡且 dense 选优，推理单卡 hybrid，严格恢复自身 checkpoint 并记录独立部署契约

#### Scenario: 机制输入协议一致

- **WHEN** hits 分析接收混合 dense 与 hybrid 部署身份的输入
- **THEN** 系统拒绝混用；同一 hybrid 协议的四份已核验预测可用于主部署 hits 分析，旧 residual 分析继续消费 dense reference

### Requirement: 当前计划和有限实证
当前活动计划 SHALL 仅保留正式 v2 M2/M3；完成状态 MUST 根据对应运行和产物的实际核验登记，不得用版本迁移、启动成功或历史 run 冒充完成。新实验 SHALL 使用统一模板及启动命令，并遵守当前研究状态中的用户授权与累计预算。

#### Scenario: 计划更新
- **WHEN** 更新正式版本计划或实验进度
- **THEN** 旧结果保留历史身份，未执行任务保持未完成，已完成任务连接其实际证据；规格迁移本身不启动实验或重置预算

### Requirement: 依赖约束的历史清理
在用户明确授权历史清理时，系统 SHALL 在保存旧配置、指标和来源后删除指定旧 CoPMRec run/artifacts，并保护基线、上游及保留 run 所依赖的产物；操作 SHALL 保存回执和真实剩余项。

#### Scenario: 发现外部消费者
- **WHEN** 待删 artifact 被保留 run 引用
- **THEN** 保留该依赖并在清理记录说明，不误删其生产者信息。

### Requirement: 正式三臂消融与固定产物诊断

消融入口 SHALL 支持原 no_mixture、no_residual、no_joint_ce 及新增 fixed_alpha_one，保留各臂自身的严格 checkpoint 身份；原三臂集合与四 bundle 机制分析 SHALL 保持原定义。机制入口 SHALL 通过统一 src.main 与 Trainer.test 执行 hits、residual、prefix 分析，不更新权重，并通过共享入口读取 keyed prediction bundle 及核验所需 checkpoint SHA256。

#### Scenario: 选择消融或机制分析

- **WHEN** 用户 compose copmrec_ablation_train、copmrec_ablation_inference 或 copmrec_diagnosis
- **THEN** 配置只能装配当前支持的臂或分析，错误臂、身份不符及无效 checkpoint 哈希被拒绝，输出由共享 writer 管理；新增训练臂不扩展原四 bundle 分析的范围

### Requirement: 精确固定 alpha 为一的训练对照

系统 SHALL 在 fixed_alpha_one 中保留三目标各权重1、共享残差及正式数据/日程/部署规则，仅将 mixture 条件概率准确固定为目录 mass；gate SHALL 冻结且不进入 optimizer，公共参数初值和 RNG SHALL 与 Full 对齐。有效 alpha 日志及 checkpoint SHALL 记录精确1及独立固定策略，默认 learned 和旧三臂 checkpoint SHALL 保持兼容。

#### Scenario: 端点损失和梯度

- **WHEN** 使用完整唯一 SID、同一 logits 与支持集计算 fixed_alpha_one
- **THEN** mixture NLL 等于 joint CE / SID 深度，总目标及关键梯度与 SID CE + (1 + 1/H) joint CE 一致，所有可训练参数梯度有限，gate 无梯度

#### Scenario: 恢复独立来源

- **WHEN** 新臂加载自身完整 checkpoint 或其他臂的 checkpoint
- **THEN** 自身 checkpoint 严格恢复且有效 alpha 仍为1，其他臂及错误 alpha 策略、固定值或 gate 状态被拒绝

### Requirement: 追加实验的可核验计划

系统 SHALL 将固定端点比较登记为 Beauty seed42 一个新增50k训练及一次自身单卡 Testing，复用已核验 Full 对照，保留旧 M2/M3 成本及完成状态。训练 SHALL 保留显式 dry-run、两种 notes 与用户 override 透传。新任务 SHALL 在实际运行核验前保持未执行，完整运行仍由用户手动启动。

#### Scenario: 准备完成

- **WHEN** 新代码、配置及计划通过聚焦验证
- **THEN** 研究状态和 Linear 准确登记对照、成本、命令、结果字段和解释边界，不填造运行ID/指标，不把实现完成当作实验完成，不自动启动实验
