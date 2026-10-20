## ADDED Requirements

### Requirement: Untied 目录监督移除具有独立身份

系统 SHALL 提供 `untied_no_joint_ce`，使用独立历史／目录残差、相同 learned gate 与原训练／部署配方，且仅移除 joint catalog CE；旧 variant 的契约和行为 MUST 保持。

#### Scenario: 损失与双表契约匹配
- **WHEN** 实例化新 variant 并计算训练损失
- **THEN** 总损失等于 SID CE 加 mixture NLL，双表均按残差 LR 优化，正式身份明确记录该 variant

#### Scenario: 拒绝跨臂恢复
- **WHEN** 新 variant 读取 Untied Full、Shared 或缺失双表的 checkpoint
- **THEN** 严格拒绝恢复；自身完整 optimizer／scheduler checkpoint 可以恢复

### Requirement: 零残差共同对照复用可审计

复用旧 `no_residual` 前系统 MUST 在 CPU 最小输入验证其与双侧冻结零参考的公共初值、RNG、多步损失／梯度／优化器／scheduler 及预测等价；复用记录 SHALL 保留旧 run、variant、输入及部署来源。

#### Scenario: 零表存储方式不改变计算
- **WHEN** 相同 seed、输入与 dropout 随机流下执行数步公共优化
- **THEN** 两种零表表示的公共训练轨迹和 dense／hybrid 预测完全一致，且无零表进入优化器

### Requirement: 固定 Untied checkpoint 生成与排序诊断

系统 SHALL 提供统一入口下的单进程 `Trainer.test` 分析，严格恢复 Untied own-best；生成条件为 learned mixture 与 alpha0合法 decoder，两种最终评分为目录 logits 与合法 decoder 完整 SID 路径 log probability。

#### Scenario: 同候选池比较最终评分
- **WHEN** 一个生成条件得到合法 beam20 与 all-cold 并集
- **THEN** 两种最终评分使用完全相同的候选池、相同合法 SID 支持和 stable catalog-row ties，真实目标不影响候选及评分

#### Scenario: 正式来源复现门禁
- **WHEN** learned mixture 加目录评分产生 Top10
- **THEN** 每个用户结果必须与冻结正式 bundle 完全相同，用户集合和来源 SHA 必须匹配，否则分析失败

#### Scenario: 分开候选覆盖与最终命中
- **WHEN** 四个预定条件完成评分
- **THEN** 输出 beam coverage、union coverage、pool size、rank、四项最终指标与 dense 参考，并将证据标为固定 checkpoint 干预，训练更新为零

### Requirement: 冻结预测贡献分析

系统 SHALL 通过 `Trainer.test` 对合法 keyed 预测和真实标签执行零模型 forward 的配对贡献分析，保留各来源真实身份；命中得失与共同命中排名贡献 MUST 加和为总 NDCG 差。

#### Scenario: 用户键重排不影响结果
- **WHEN** 不同预测 bundle 的用户行顺序不同
- **THEN** 按用户 key 对齐后计算同一用户差值，拒绝缺失、重复或额外用户及非法／重复候选

#### Scenario: 配对统计与贡献一致
- **WHEN** 输出四指标差值及95%用户配对区间
- **THEN** 使用 PCG64 seed42和2000次默认抽样，明确方向与分母，并核验贡献加和；区间不解释为训练 seed 稳定性

### Requirement: 配置、入口和输出遵守现有运行契约

新能力 MUST 通过 `src.main` 与 Hydra experiment、共享 Artifact loader、共享 structured writer 和 `paths.output_dir` 执行；根脚本 SHALL 支持显式 dry-run、两种 notes、额外 override 及错误输入检查。

#### Scenario: 准备不触发正式运行
- **WHEN** 完成配置 compose、CPU 测试及脚本验收
- **THEN** 新训练／Testing／远端模型 forward 仍为零，Linear 将实现准备和待执行实验分开记录，多数据集／多 seed 任务后移且原 Done 保留
