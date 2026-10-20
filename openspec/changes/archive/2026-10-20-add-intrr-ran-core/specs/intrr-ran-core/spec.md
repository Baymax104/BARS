## ADDED Requirements

### Requirement: 共享递归分配

系统 SHALL 提供独立 RAN，使用每层可训练 codebook 与层间 MLP，按原指导向量及上一层 codeword 递归计算 logits。

#### Scenario: 核准递归输出
- **WHEN** 使用固定小型 codebook、MLP 和指导向量运行两层 RAN
- **THEN** logits 与手工逐层计算一致，商品输出等于各层所选 codeword 之和

### Requirement: 作者 STE 与目标前缀监督

系统 MUST 保留商品侧 hard-forward/soft-backward 梯度，用户侧 teacher forcing 只能读取当前层之前的真实 SID。

#### Scenario: STE 梯度
- **WHEN** 对商品组合表示反向传播
- **THEN** 前向等于 hard codeword，指导向量和 codebooks 获得有限梯度

#### Scenario: 无未来目标泄漏
- **WHEN** 修改某层或后续层的真实 SID
- **THEN** 该层和更早层 logits 不变，下一层可以随前一层真实 codeword 改变

### Requirement: 输入验证

系统 MUST 对不匹配的层数、codebook 范围、浮点 SID 或维度给出明确错误。

#### Scenario: 非法 SID
- **WHEN** teacher forcing 输入含越界或非整数 SID
- **THEN** 运行明确失败，不截断或静默修正
