## ADDED Requirements

### Requirement: 来源适配与整数身份
系统 SHALL 提供 Steam、Amazon 2014 Adapter，将商品 metadata 和事件转换为共同记录，持久化可逆的确定整数映射；SHALL NOT 修改模型输入接口或现有运行入口。

#### Scenario: 相同源身份重复准备
- **WHEN** 相同源文件及配置在不同输出目录准备
- **THEN** 商品、用户映射及 TFRecord 内容 MUST 一致，商品0保持真实商品 key。

#### Scenario: Steam 用户与内容
- **WHEN** Steam 原生 user_id 缺失或评论有 text 字段
- **THEN** MUST 使用 username 作为源身份，商品文本 MUST 只来自 metadata。

### Requirement: 图过滤与共同切分
系统 SHALL 按唯一邻居迭代计算 5-core，默认保留重复事件，按 UTC 时间和源行号稳定排序，最后两事件依次作为验证、测试目标。SHALL 将历史截断、SID 和 padding 交给原有消费链路。

#### Scenario: 重复评论不提高图度数
- **WHEN** 用户对一个商品存在五条事件
- **THEN** 该用户的唯一商品邻居数 MUST 为一，重复事件 MUST NOT 使其满足 5-core。

#### Scenario: 序列留出
- **WHEN** 过滤后序列为 a,b,c,d,e
- **THEN** training MUST 为 a,b,c，evaluation MUST 为 a,b,c,d，testing MUST 为 a,b,c,d,e，三个 split 用户 key MUST 一致。

### Requirement: 文件契约与完整性
输出 SHALL 为 gzip TFRecord Example，商品包含整数 id 和 bytes text，序列包含整数 user_id 和 sequence_data。系统 SHALL 回读校验行数、映射、标签前缀、目录覆盖与分片覆盖，成功后原子发布，既有目录 SHALL NOT 被覆盖。

#### Scenario: 分布式读取
- **WHEN** 配置指定 rank 和 worker 数
- **THEN** 每个 split MUST 包含足够非空分片，避免共享文件或无文件 worker。

#### Scenario: 失败的准备
- **WHEN** 存在未知商品、冲突内容或校验错误
- **THEN** MUST 不发布完成目录，原始数据 MUST 保留。

### Requirement: 协议与来源登记
manifest SHALL 记录源与产物哈希、代码指纹、过滤/重复/切分/采样规则及计数。默认 Steam SHALL 不采样，stride7 SHALL 使用独立 profile 和协议名称。

#### Scenario: 子采样身份
- **WHEN** 使用 Steam stride7 profile
- **THEN** MUST 记录采样顺序和阶段，MUST NOT 将其宣称为与原论文逐用户一致的复现。

### Requirement: 有界 dry-run
独立准备命令 SHALL 支持显式记录上限的 dry-run，使用相同转换/写出/回读流程及临时目录，不发布正式输出、不实例化模型、不连接 W&B。

#### Scenario: 真实源 dry-run
- **WHEN** 在 node1 指定 dry-run 和记录上限
- **THEN** MUST 记录实际读取数与 sample 标记；非空 core 及校验通过才能成功，样本不满足 core MUST 明确失败而不是自动改变协议。

### Requirement: LETTER 新数据集入口
LETTER 启动器 SHALL 接受 steam 和 home_and_kitchen，并保持已有参数、override 和模型接口。

#### Scenario: 新数据集参数
- **WHEN** 通过 LETTER 脚本传入上述名称
- **THEN** MUST 将其作为 dataset_name 透传，不因旧白名单拒绝。

### Requirement: 新数据集 UTF-8 文本读取
新数据集 embedding 运行 SHALL 显式选择严格 UTF-8 解码适配函数，保持文本数组形状、商品 key 和模型输入接口。旧数据集默认预处理配置 SHALL 不变。

#### Scenario: 商品文本包含非 ASCII 字符
- **WHEN** 商品文本包含重音字母、中文或 Unicode 符号
- **THEN** MUST 完整解码原字符并交给既有 tokenizer，MUST NOT 丢弃字符或替换乱码；非法 UTF-8 MUST 明确失败。
