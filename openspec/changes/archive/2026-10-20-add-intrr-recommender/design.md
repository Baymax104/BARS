## Context

依赖已完成的 `add-intrr-ran-core`。作者代码的活跃路径为商品 UID（512维）经投影至256维，用共享 RAN 压成一个历史 token，输入4层 causal T5Stack；最后有效 hidden 经同一 RAN 预测 SID。没有额外 content 特征输入、BOS、separator、absolute position embedding、catalog scorer 或 cold union。

## Goals / Non-Goals

目标是接入原生 IntRR 算法并精确复用 TIGER 的输入信息和公共基础设施。非目标是复刻作者不同的数据增强、优化器、320k预算、多backbone/tokenizer矩阵或运行正式实验。

## Decisions

- 新增 `IntrrCatalog`，只通过公共 `load_model_output` 读取 keyed SID bundle。按key排序产生compact UID，前H列SID必须唯一，sha256绑定key/SID/维度。
- `CompressTigerHistory` 仅追加于原TIGER预处理末端：保持原标签/采样，完整SID组转UID，去除唯一目标占位及全padding组，右padding到 `sequence_length // H - 1`。180/H4对应44历史商品，真实包含0的完整SID仍有效。
- 沿用 `TigerModelInput`、`TigerLabelData` 和现有collate；IntRR把 `input_ids` 解释为compact UID，padding=-1。catalog建立反向SID查找，不用max key推导embedding行数。
- 通过 `intrr_collate` 在完整原TIGER预处理之后应用压缩，再委托原 `collate_fn_sequence`；这样配置可直接继承TIGER，无需复制或重写采样流水线。
- 模型内部采用作者活跃 T5Stack 和 FF 多层结构；不搬运未使用encoder等dead分支。cross-attention未被调用，其参数冻结，避免DDP未使用梯度。
- UID先去重运行RAN，再还原历史位置；alignment逐位置平均、逐层求和，保留重复商品频次权重。推荐CE同样逐层求和。默认alignment=0.1与论文及作者构造函数一致，公开YAML为0.0差异在来源说明登记；允许模型内部override。
- 合法prefix在softmax之前屏蔽，与TIGER和作者实现一致；beam累加log probability，不能以每层greedy替代；处理早层合法分支少于beam的情况，最终仅返回有限、合法且唯一的完整SID。
- checkpoint绑定目录、模型结构、输入长度和算法版本。train/eval/predict复用统一入口及metric callback，优化器由TrainingModelConfig注入，不在模块中定义学习率或预算。

## Risks / Trade-offs

当前TIGER与作者增强不同 → 完整继承TIGER流水线并用相同随机种子的样本对齐测试验证。大词表beam早层可能不足 → 覆盖窄树和全枚举参考。T5版本和dead参数可影响DDP → CPU有效参数梯度测试，后续模块做有界node1验证。
