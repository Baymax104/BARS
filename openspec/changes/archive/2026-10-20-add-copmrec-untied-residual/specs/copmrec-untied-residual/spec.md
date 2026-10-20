## ADDED Requirements

### Requirement: 历史与目录独立残差

系统 SHALL 提供 untied_residual 变体，使用两张同维、独立存储、全零初始化的商品残差表，分别用于历史编码和目录评分；内容投影和其余网络保持共享，两侧注入位置及scale=1保持原定义，cold两侧残差恒零。

#### Scenario: 分别修改两侧参数

- **WHEN** 仅修改history表或catalog表的seen行
- **THEN** history表只直接影响历史编码，catalog表只直接影响固定query下的目录评分；两张表均可独立学习，cold输出及更新后权重保持零

### Requirement: 匹配初始化与优化协议

系统 SHALL 保持与同seed Full一致的公共参数初值、构造及初始forward RNG、三目标各权重1和learned alpha。两张残差表 SHALL 恰好各进入残差LR0.002参数组一次，基础LR0.0003、AdamW wd0.035、warm2500/cosine50000及50k scratch保持原协议。

#### Scenario: 对齐公共初值与梯度

- **WHEN** 用相同seed构造Full与Untied并在同一小batch和RNG下计算初始损失
- **THEN** 公共state、各项损失和forward后RNG匹配，Full残差梯度等于两张独立残差梯度之和，optimizer不把任一残差表归入基础LR组

### Requirement: 双表独立checkpoint身份与完整恢复

Untied SHALL 记录独立variant、残差sharing与protocol，完整保存两张表及对应optimizer moments和scheduler。自身checkpoint SHALL 严格恢复，拒绝Full/其他变体、缺失参数或moments、错误LR组、非法state及cold非零；旧shared/原三臂/fixed_alpha_one契约保持兼容。

#### Scenario: 恢复后继续更新

- **WHEN** 从两次CPU优化后的自身完整checkpoint恢复模型、optimizer和scheduler
- **THEN** 下一次相同batch更新与连续运行匹配，跨变体或损坏的双表/optimizer状态被拒绝

### Requirement: 有界实验准备与证据范围

系统 SHALL 仅登记Beauty seed42一次新增50k scratch训练和一次自身own-best的单卡hybrid Testing计划，复用既有Shared Full，按训练内dense Validation首次最佳NDCG@10选点。内容/SID/数据和候选排序协议保持匹配，主指标为hybrid NDCG@10并完整报告R5/N5/R10及用户配对区间和参数增量。实现完成 SHALL 与实验完成分开，不自动启动训练或扩展预算。

#### Scenario: 本地实现准备完成

- **WHEN** 新变体、配置/脚本和聚焦验证完成
- **THEN** 研究状态仍为prepared_not_started，新增run/checkpoint/指标为空，保留旧650k花费及hybrid13+1闭环，提供手动命令和正向/负向/不确定结果处理规则
