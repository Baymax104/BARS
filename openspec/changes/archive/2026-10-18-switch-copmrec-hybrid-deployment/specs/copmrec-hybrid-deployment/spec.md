## ADDED Requirements

### Requirement: 独立 hybrid 主部署契约

系统 SHALL 默认采用 hybrid 预测，声明独立 `copmrec-hybrid-deployment-v1` 契约；正式配置 SHALL 使用20条 beam、所有 cold 商品并集、去重和候选内 joint catalog logits 稳定排序，无历史排除。系统 SHALL 保留显式 dense 辅助预测并准确标注其全目录候选池，不改变标准 keyed prediction bundle schema。

#### Scenario: hybrid 候选重排

- **WHEN** beam 包含重复或非法行，cold 商品未进入生成候选
- **THEN** 非法行被丢弃，合法生成与所有 cold 行去重后稳定重排，不从全目录额外补入 seen 商品；候选中的历史商品仍可被推荐

#### Scenario: 显式 dense 辅助

- **WHEN** 用户显式选择 dense 预测
- **THEN** 使用原完整目录稳定排序，运行元信息声明 dense 和 all_catalog，而非 hybrid

### Requirement: 候选 alpha 策略准确继承

系统 SHALL 使用实例的 candidate processor 动态分派；Full 使用自身 checkpoint 学得的全局 alpha，no_mixture 使用冻结0.5，fixed_alpha_one 使用精确1端点且不读取 sigmoid(0)作为候选权重。产物 SHALL 记录实际策略与来源。

#### Scenario: 固定与可学习策略

- **WHEN** 分别恢复 Full、no_mixture 或 fixed_alpha_one 的 own-best
- **THEN** 候选采用各自的正确策略，兼容构造字段0.5不覆盖学得的值，固定1直接使用 mass 条件概率

### Requirement: 正式迁移的有限执行范围

系统 SHALL 将用户授权的新增范围记为9次 Full、3次消融、1次 fixed-alpha-one 正式推理及1次 hits 分析，新增训练为零；临时比较 SHALL NOT 替代正式产物，迁移 SHALL NOT 重置已消耗预算或宣称计算效率改善。

#### Scenario: 登记迁移结果

- **WHEN** 正式推理尚未完成或产物未核验
- **THEN** 对应矩阵单元保持未完成，原 dense 与临时结果保留其各自身份
