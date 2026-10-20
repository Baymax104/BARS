# intrr-recommender Specification

## Purpose
定义 IntRR 的商品目录适配、历史编码、共享监督、合法 SID 生成及严格 checkpoint 身份。
## Requirements
### Requirement: TIGER 样本与历史信息保持一致

系统 MUST 复用TIGER采样、目标和SID级截断，仅压缩完整历史SID组为商品UID，并保留预测user key。

#### Scenario: 同seed采样一致
- **WHEN** 相同raw row经原TIGER预处理及追加IntRR适配运行
- **THEN** 每条目标SID和适配前后的历史商品完全一致，180slots最多44历史商品

#### Scenario: 真实零code与坏SID
- **WHEN** 完整历史SID含0或出现半残SID
- **THEN** 完整含0SID保留，半残或目录未知SID明确失败

### Requirement: 共享RAN推荐与监督

系统 SHALL 使用同一RAN处理商品UID和用户状态，以causal T5单商品token历史建模；训练MUST计算逐层推荐CE与按历史位置平均的SID alignment。

#### Scenario: 监督梯度与出现次数
- **WHEN** 使用含重复商品的最小batch训练计算loss
- **THEN** alignment与手工逐位置参考相等，UID、RAN和causal backbone均有有限梯度

### Requirement: 原生合法SID beam生成

系统 MUST 在合法子分支归一化后累加路径log probability进行beam搜索，返回完整SID，使用全目录、无历史排除及无cold额外并入。

#### Scenario: 窄树与穷举参考
- **WHEN** beam覆盖完整小型目录且早层合法分支少于beam
- **THEN** 最终SID及分数与独立逐路径枚举一致，无非法、重复或非有限候选

### Requirement: 公共接口与严格恢复

系统 SHALL 通过Lightning train/validation/test/predict接口和ModelOutput接入公共metric/writer；checkpoint MUST 核验目录与结构身份。

#### Scenario: 恢复与输出
- **WHEN** 同身份checkpoint恢复并预测
- **THEN** 输出keys对应user且predictions为完整SID；更换目录或结构恢复明确失败
