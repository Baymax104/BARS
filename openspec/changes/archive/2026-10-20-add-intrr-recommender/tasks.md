## 1. 数据适配

- [x] 1.1 实现keyed SID目录与TIGER末端压缩适配。
- [x] 1.2 验证采样/历史/目标一致、padding/零code和非法输入。

## 2. 推荐模型

- [x] 2.1 实现作者causal T5、多层FF、UID与共享RAN及监督。
- [x] 2.2 实现合法SID beam、Lightning接口及checkpoint身份。
- [x] 2.3 验证梯度、alignment权重、穷举beam与恢复。

## 3. 集成核验

- [x] 3.1 运行本模块CPU测试及相关公共协议回归。
- [x] 3.2 运行OpenSpec strict验证并记录实际结果。

验证：IntRR RAN、backbone/module、data 与既有 TIGER metric、prediction callback、preprocessing 聚焦集成回归共107项通过；相关文件ruff与 `openspec validate add-intrr-recommender --strict` 通过。
