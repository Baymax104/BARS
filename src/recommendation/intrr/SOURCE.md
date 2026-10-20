# IntRR 实现来源

本目录的递归分配机制改编自作者公开实现：

- 仓库：[DreamX-Rec/IntRR](https://github.com/DreamX-Rec/IntRR)。
- 固定 commit：`806e0f1969ed61a0748902649b335c0ea066de00`。
- 核心参考：[intrr_decoder_only_model.py，`codebook_ran_module` 与 `codebook_ran_module_infer`](https://github.com/DreamX-Rec/IntRR/blob/806e0f1969ed61a0748902649b335c0ea066de00/src/models/modules/semantic_id/intrr_decoder_only_model.py)。
- 论文：[IntRR: A Framework for Integrating SID Redistribution and Length Reduction](https://arxiv.org/abs/2602.20704)。

实现按公开代码保留每层随机初始化 codebook、共享层间 MLP、`[previous_code, guidance]` 拼接、codeword 求和，以及 hard-forward/soft-backward STE。论文描述的 soft 组合与该代码存在版本差异，本实现选择固定 commit 的执行行为。teacher forcing 仅读取前一层目标。temperature 仅影响 STE soft 分配，监督和 beam 使用原始点积 logits。

接口拆分与输入校验适配当前 GRID 框架；作者代码的可选分离 MLP、输入投影与可学习 temperature 不属于本核心接口。

## 推荐模型接入选择

- 保留作者活跃的 UID-only 输入：512维 UID 经线性映射至256维，共享 RAN 将一个商品压成一个 token，4层 causal T5 产生最后有效 hidden，再由同一 RAN 预测 SID；不搬运未调用的 encoder 或原 SID 输出头。
- T5 内部默认 `num_heads=6`、`d_kv=64`、`d_ff=1024`、dropout 0.15；FF 精确顺序为 `Linear(d,ff) → ReLU → Linear(ff,ff) → Dropout → ReLU → Linear(ff,d) → Dropout`，外层保留 pre-norm、Dropout 和残差。最后线性层后没有 ReLU。
- 按作者 wrapper 对 T5 子模块递归调用默认 `reset_parameters`，以普通 Linear 初始化重置 attention；再替换 FF。没有 encoder states 的 cross-attention 参数冻结，其计算不参与前向。
- 推荐 CE 与历史 SID alignment 都逐层求和；alignment 按有效历史位置平均，重复商品按出现次数加权。默认 `alignment_weight=0.1` 与论文及作者 Python 构造函数一致，作者公开 YAML 使用 `0.0`，该差异通过显式模型配置记录。
- 合法 prefix 在 softmax 前屏蔽，beam 累加条件 log probability。训练采样、历史信息、优化器、步数、评价选点和 logger 采用当前 TIGER 公共协议，不能将作者 YAML 的外部协议混入本基线。

## 上游许可全文

```text
MIT License

Copyright (c) 2026 Alibaba Group

Portions of this code are based on the GRID (Generative Recommendation with Semantic IDs) framework by Snap Research.
Original GRID project: https://github.com/snap-research/GRID
Original GRID License: MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

We express our sincere gratitude to the Snap Research team for their open-source contributions to the generative recommendation community.
```
