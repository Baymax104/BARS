## Context

作者公开代码固定为 `806e0f1969ed61a0748902649b335c0ea066de00`。RAN 包含每层可训练 codebook 与层间 `Linear(2d,h) → ReLU → Linear(h,d)`；同一实例用于商品和用户。现有框架已有 torch/transformers，无需依赖变更。

## Goals / Non-Goals

目标：以小型张量核准递归、STE、逐层 logits 与 teacher forcing 的行为。非目标：本模块不读取数据、不构建 Trainer、不定义外部训练预算或增加 baseline 变体。

## Decisions

- 按作者公开代码的 STE 执行，保留 soft 分配梯度，前向选 hard codeword；论文的 soft 描述作为已知版本差异记录，不混称逐字复刻论文。
- 逐层 logits 为 hidden 与该层 codebook 的点积，层间输入拼接原指导向量与前层 codeword。
- 商品侧使用预测 codeword 递归并将各层 codeword 求和；用户监督侧仅以前一层真实 codeword 递归，当前/未来目标不能进入当前层 hidden。
- 核心以显式方法暴露 embedding/logits/逐层状态，供后续模块共用一套参数与测试监督路径。
- 代码按 MIT 来源保留作者 attribution；接口遵守当前命名与张量约定。

## Risks / Trade-offs

STE 与论文纯 soft 描述有差异 → 固定公开代码版本并做数值参考测试。形状或递归错误可能仍能训练 → 用手工 codebook、小张量和梯度测试先核准。
