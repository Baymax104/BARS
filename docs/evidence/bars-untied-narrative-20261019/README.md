# Untied Beauty42 与 LIGER／LETTER 的直接用户配对复算

日期：2026-10-19。仅读取 node1 已存在的冻结预测与标签，不创建 W&B run，不训练、不运行 Testing、不调用模型 forward、不下载 Artifact。`baseline-paired-comparison.json` 为完整精度结果，`baseline-pair-sources.json` 固定输入路径及预期字节哈希，结果 `sources` 记录实际 SHA256 与文件大小。

## 输入与独立核验

- Untied：训练 `g953gzcq`、自身 own-best step39500、Test `e4a3b038`。原预测 SHA256 为 `f15c09e0464de7f33eeb9eeabe00f55758f51028d088c923f48b4257ece0ca93`。
- LIGER：保留原 hybrid Test `042139al`；原生 SID 经同一冻结、完整唯一的 canonical SID 字典转为商品 key；没有重排或改写部署规则。
- LETTER：保留 Test `wvpeeti8`，直接使用原始商品 key Top10；未将 LETTER SID 当成 BARS SID。
- 22363 个用户严格对齐。真实 SID 标签同时与旧 Untied 配对 NPZ、冻结 `beauty-user-statistics.npz` 的用户及目标商品 key 互核；Untied 从原预测重新计算的 rank 与旧 NPZ 逐用户完全一致。
- 三模型 Top10 均合法、唯一。指标分别用 rank 公式和直接命中矩阵计算，两种方法完全一致；均值与原冻结结果误差小于 `1e-12`。
- Bootstrap 主算法按用户差值采样；独立算法重置相同随机流，用抽样人数向量逐次重放全部 2000 次。最大差异为 `8.673617379884035e-17`。

## 结果

PCG64 seed42、2000 次、95% pointwise 用户配对 bootstrap，NumPy linear quantile；方向为 Untied−baseline，相对分母为 baseline；不做多重比较校正。

| baseline | 指标 | Untied−baseline | 95% CI | 相对提升 |
| --- | --- | ---: | --- | ---: |
| LIGER hybrid | Recall@5 | 0.016589902964718507 | [0.013413897956445915, 0.01954120645709431] | 43.957345971563974% |
| LIGER hybrid | NDCG@5 | 0.014682304236388862 | [0.012358729835426343, 0.016899255526164184] | 61.17722440051606% |
| LIGER hybrid | Recall@10 | 0.019451773017931405 | [0.015963868890578187, 0.02285024370612172] | 34.77218225419664% |
| LIGER hybrid | NDCG@10 | 0.015601829782023964 | [0.013280300842776621, 0.01779361278758874] | 52.23682070856416% |
| LETTER | Recall@5 | 0.015024817779367705 | [0.012071278451012834, 0.018020837991324958] | 38.22525597269624% |
| LETTER | NDCG@5 | 0.012988726570426448 | [0.010914604120512466, 0.015129457909396451] | 50.55316345265012% |
| LETTER | Recall@10 | 0.015382551536019317 | [0.012118231006573358, 0.018602155345883827] | 25.63338301043219% |
| LETTER | NDCG@10 | 0.013104915002412705 | [0.010984988342050214, 0.015298616413506326] | 40.49174731097387% |

所有区间均高于零。范围仅为 Beauty／training seed42、各自已选 checkpoint 的用户抽样；不代表训练 seed 不确定性，也不建立残差、目录 CE 或 mixture 的单独因果贡献。LIGER 和 LETTER 继续保留各自原生上游、部署及历史政策。

## 复现

从 GRID 根目录执行：

```powershell
./docs/evidence/bars-untied-narrative-20261019/run-baseline-pair-audit.ps1
```

脚本仅通过 SSH 将审计 recipe 发送到 node1，在仓库根目录通过现有 `uv run --no-sync` 运行纯文件读取与统计，JSON 回传本目录。未修改 node1 代码、配置或依赖。

论文主线、贡献与证据分工见[Untied叙事记录](../../../../research/docs/bars-untied-narrative-20261019.md)。文档数字、来源身份、YAML、链接和审计recipe一致性通过74项检查，见[验收结果](narrative-validation.json)；历史状态块保持、当前叙事指针及新记录分别登记。
