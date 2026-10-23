## MODIFIED Requirements

### Requirement: 固定 Untied checkpoint 生成与排序诊断

系统 SHALL 提供统一入口下的单进程 `Trainer.test` 分析，严格恢复 Untied own-best。当前来源 MUST 为固定alpha0.5、无mixture loss的Full，生成条件为production mixture与alpha0合法decoder，两种最终评分为目录logits与合法decoder完整SID路径log probability。显式历史learned-alpha来源 SHALL 保留其真实身份和复现能力。

#### Scenario: 同候选池比较最终评分
- **WHEN** 一个生成条件得到合法beam20与all-cold并集
- **THEN** 两种最终评分使用完全相同的候选池、相同合法SID支持和stable catalog-row ties，真实目标不影响候选及评分

#### Scenario: 正式来源复现门禁
- **WHEN** production mixture加目录评分产生Top10
- **THEN** 每个用户结果必须与指定来源的冻结正式bundle完全相同，用户集合和来源SHA必须匹配，否则分析失败

#### Scenario: 分开候选覆盖与最终命中
- **WHEN** 四个预定条件完成评分
- **THEN** 输出beam coverage、union coverage、pool size、rank、四项最终指标与dense参考，元数据记录真实固定或learned alpha，证据标为固定checkpoint干预且训练更新为零
