# bars-main-design-selection Specification

## Purpose
定义固定半混合、两损失 Untied 主方法及角色隔离。角色迁移和1/9回退场景只记录主版本切换时点；后续 hybrid 重训与验收覆盖以当前结果回执为准，不要求将已完成矩阵回退。

## Requirements
### Requirement: 当前 BARS 主版本选择

系统 SHALL 将 Untied、固定 alpha=0.5、SID CE 与 Catalog CE 权重1、mixture NLL权重0作为当前主方法设计，沿用已验收 variant 身份。

#### Scenario: 当前主方法配置装配
- **WHEN** 选择 untied_fixed_alpha_half_no_mixture 训练或推理
- **THEN** 显示组为 bars_main，alpha固定0.5，两套residual独立，训练损失权重为1/1/0

### Requirement: 运行角色迁移与历史保护

系统 SHALL 将旧 bars_main 的18条记录转入 history，将已验收的新Beauty42训练和两种测试转入bars_main，保持配置、指标、身份及Artifact不变。

#### Scenario: 显示元数据迁移
- **WHEN** 完成旧主矩阵与新Beauty42角色切换
- **THEN** bars_main包含新3条记录、history包含原18条记录，保护字段与产物前后相同

### Requirement: 新主矩阵覆盖和待执行状态

系统 SHALL 以新版本1/9覆盖回退M2父项及其余8格为Todo，保留Shared对照Done和旧实验历史，不从状态回退推导启动授权。

#### Scenario: M2回退
- **WHEN** 新Beauty42被选为主方法来源
- **THEN** 8个其他新版本单元尚无run或checkpoint，父项标记1/9，当前命令使用新变体且无新训练启动
