## MODIFIED Requirements

### Requirement: 正式三臂消融与固定产物诊断

消融入口 SHALL 支持原 no_mixture、no_residual、no_joint_ce 及新增 fixed_alpha_one，保留各臂自身的严格 checkpoint 身份；原三臂集合与四 bundle 机制分析 SHALL 保持原定义。机制入口 SHALL 通过统一 src.main 与 Trainer.test 执行 hits、residual、prefix 分析，不更新权重，并通过共享入口读取 keyed prediction bundle 及核验所需 checkpoint SHA256。

#### Scenario: 选择消融或机制分析

- **WHEN** 用户 compose copmrec_ablation_train、copmrec_ablation_inference 或 copmrec_diagnosis
- **THEN** 配置只能装配当前支持的臂或分析，错误臂、身份不符及无效 checkpoint 哈希被拒绝，输出由共享 writer 管理；新增训练臂不扩展原四 bundle 分析的范围

## ADDED Requirements

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
