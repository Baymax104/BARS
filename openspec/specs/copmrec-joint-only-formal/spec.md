# copmrec-joint-only-formal Specification

## Purpose
定义正式 BARS 联合视图的三目标训练、全阶段无历史排除和严格版本身份，明确统一入口、固定日程及可核验来源，避免将历史 checkpoint 改标签作为新的正式训练。
## Requirements
### Requirement: 正式联合视图训练目标

系统 SHALL 在新正式入口仅优化 SID CE、完整目录 joint CE、mixture NLL，各权重为1；SHALL 保留共享历史与目录商品残差、内容投影、训练cold规则和固定50k双卡日程，不构建native目录评分或native CE。

#### Scenario: 与已有A3计算对齐

- **WHEN** 固定同一参数、输入与dropout随机数
- **THEN** 三项损失、总损失和参数梯度与A3一致；joint CE 对seen商品残差有有限非零梯度，cold残差梯度为零

### Requirement: 全阶段不排除历史商品

系统 SHALL 在训练目录支持集、raw dense Validation 及最终单卡 hybrid 推理中保留历史商品，继续使用完整历史输入和残差。hybrid SHALL 在生成与全部 cold 的候选并集内使用稳定 catalog-row 排名；显式 dense 辅助推理 SHALL 保留原全目录稳定排名。Validation 及 own-best 选点 SHALL 继续使用 dense。

#### Scenario: 历史商品位于候选中且分数最高

- **WHEN** 合法历史商品进入 hybrid 候选且原始 joint 分数位于候选 TopK
- **THEN** hybrid 推理保留该商品，排序不读取目标标签；dense Validation 与显式 dense 辅助继续保留完整目录内的历史商品

### Requirement: 独立可核验来源

系统 SHALL 保存严格的新正式版本契约和完整模型/optimizer/scheduler状态，拒绝将原Full或A3checkpoint改标签当作新的正式训练；SHALL 保留其已有实证供明确标注的选型分析。既有正式 v2 own-best SHALL 按其原训练契约严格恢复用于 hybrid 或显式 dense，部署差异 SHALL 由独立运行契约记录，不能改写旧 checkpoint 身份。

#### Scenario: 恢复来源不同

- **WHEN** 新入口收到旧Full、A3或不同版本/损失契约的checkpoint
- **THEN** 拒绝普通正式恢复；正式 v2 自身完整 checkpoint 可恢复，在相同部署模式下预测一致

#### Scenario: 切换已有正式权重的部署

- **WHEN** 用户将自身已验证 v2 own-best 交给 hybrid 预测
- **THEN** 模型状态严格恢复，原训练来源与文件SHA不变，发布独立 hybrid 部署身份

### Requirement: 入口及研究状态一致

系统 SHALL 提供统一src.main的双卡训练/单卡推理根脚本，透传两种notes、dry-run和额外override，记录方法/损失/历史协议，并同步研究和Linear最新定义；规格迁移本身 SHALL NOT 授予额外实验预算。

#### Scenario: 版本冻结完成

- **WHEN** 新代码通过CPU测试、Hydra compose、shell验证及OpenSpec strict验证
- **THEN** 报告实现完成与已有选型结果，不把未启动正式实验标记完成、不重置旧任务/成本、不自动启动新运行
