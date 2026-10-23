# IntRR Sports 三 seed Testing 结果

2026-10-20按用户指令，对已完成训练的Sports三个seed各执行唯一一次自身best全量Testing，三个独立审计均通过。

| seed | own-best step | R@5 | N@5 | R@10 | N@10 | Testing run |
|---|---:|---:|---:|---:|---:|---|
| 42 | 49700 | 0.01783808 | 0.01148451 | 0.02741727 | 0.01457375 | [jza1eqyq](https://wandb.ai/baymaxam/GRID/runs/jza1eqyq) |
| 200 | 49700 | 0.01677061 | 0.01088034 | 0.02550705 | 0.01369500 | [evhdgof7](https://wandb.ai/baymaxam/GRID/runs/evhdgof7) |
| 2026 | 49400 | 0.01851228 | 0.01209094 | 0.02727681 | 0.01492450 | [alhv8dw4](https://wandb.ai/baymaxam/GRID/runs/alhv8dw4) |
| mean ± std | — | 0.01770699 ± 0.00087820 | 0.01148526 ± 0.00060530 | 0.02673371 ± 0.00106464 | 0.01439775 ± 0.00063336 | ddof=1 |

数值为比例；每格35,598用户，完整合法唯一Top10，双writer一致，源码与checkpoint字节及SID lineage核验通过。原始TFRecord独立复算四指标，与W&B最大绝对误差低于3.3e-17。checkpoint按完整500次Validation首次最高NDCG@10选取，不使用Testing选点。

三seed均值及样本标准差描述Sports训练seed变化，不表示用户置信区间。Beauty已完成三seed，本轮后IntRR完整矩阵6/9；Toys42在GPU4/5继续原训练，已核验至少44,900步，Toys200／2026仍排队。没有新增训练格、训练重试、调参或上游运行。

实际Testing使用GPU1／6／7各一张，经原intrr_inference.sh和统一src.main执行，FP32、batch32、workers8、合法beam10、全目录且无历史过滤；三格各一次正式Testing。本轮没有改变模型、训练或评价协议。

全部来源、输入审计hash及三seed汇总见[证据目录](evidence/intrr-sports-test-20261020/README.md)。表格直接由其three-seed-summary.json生成。
