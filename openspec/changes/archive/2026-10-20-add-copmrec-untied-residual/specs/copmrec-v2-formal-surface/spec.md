## MODIFIED Requirements

### Requirement: 正式三臂消融与固定产物诊断

消融入口 SHALL 支持原 no_mixture、no_residual、no_joint_ce、fixed_alpha_one 及新增 untied_residual，保留各臂自身的严格 checkpoint 身份；原三臂集合与四 bundle 机制分析 SHALL 保持原定义。机制入口 SHALL 通过统一 src.main 与 Trainer.test 执行 hits、residual、prefix 分析，不更新权重，并通过共享入口读取 keyed prediction bundle 及核验所需 checkpoint SHA256。

#### Scenario: 选择消融或机制分析

- **WHEN** 用户 compose copmrec_ablation_train、copmrec_ablation_inference 或 copmrec_diagnosis
- **THEN** 配置只能装配当前支持的臂或分析，错误臂、身份不符及无效 checkpoint 哈希被拒绝，输出由共享 writer 管理；新增训练臂不扩展原四 bundle 分析的范围
