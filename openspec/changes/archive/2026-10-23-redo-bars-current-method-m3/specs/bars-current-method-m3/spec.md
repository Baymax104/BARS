## ADDED Requirements

### Requirement: 当前配方匹配组件臂

系统 SHALL 提供独立的当前 Shared、双侧零残差和去 Catalog CE 变体。三者 MUST 固定alpha0.5、无mixture训练权重、hybrid Validation与唯一推荐协议，记录独立变体和当前M3协议；旧变体行为 MUST 保持。

#### Scenario: 同配方消融与严格恢复
- **WHEN** 构造三个当前变体并执行最小训练更新及恢复
- **THEN** Shared及零残差loss为SID CE加Catalog CE，去CE总loss为SID CE；零表冻结且不进优化器，去CE参数梯度/Adam状态有效；各自完整checkpoint可以恢复并拒绝跨臂恢复

#### Scenario: 配置与根脚本一致
- **WHEN** compose当前变体并通过根脚本传入notes、dry-run与额外override
- **THEN** 解析得到固定alpha0.5、hybrid选点、对应loss和协议，用户override在默认值之后生效，错误值被拒绝

### Requirement: 当前来源与进度独立登记

当前机制覆盖 MUST 排除旧三损失与dense选点结果；Full可复用当前已验收来源，其余三臂 SHALL 独立重训。预算、历史完成事实、来源及结果解释 MUST 分开记录。

#### Scenario: 当前M3重新开始
- **WHEN** 按用户要求回退M3
- **THEN** 当前执行任务重回待完成，旧描述与关系有快照，旧结果仅供追溯，Shared/零残差不因旧Done跳过训练
