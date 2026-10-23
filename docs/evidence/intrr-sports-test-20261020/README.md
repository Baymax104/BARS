# IntRR Sports 三 seed 自身最佳 checkpoint Testing

用户在2026-10-20要求将已完成的训练进行下一步。核准 Sports／seeds42、200、2026 已完成50k、完整500次验证及正常退出后，各执行唯一一次自身best全量Testing。Toys三格继续原训练队列，不新增训练单元或重试。

## 冻结选点与运行

| seed | 训练run | 首次最高val/NDCG@10的步数 | Testing run | 物理GPU |
|---|---|---:|---|---:|
| 42 | dcgyc6s2 | 49,700 | jza1eqyq | 1 |
| 200 | t36o8gnd | 49,700 | evhdgof7 | 6 |
| 2026 | htszjufh | 49,400 | alhv8dw4 | 7 |

逐格checkpoint SHA256、严格contract、不可变v0 Artifact及digest均核准。Testing经原intrr_inference.sh和统一src.main，在独立tmux中并行执行三个单卡任务；各自batch32、workers8、FP32、合法beam10、全目录且无历史过滤，沿用原TIGER通用协议。源SID固定jcyr5l3p:v0，不重跑上游。

Mutagen flush成功，三个session均Watching且无conflict；实际源码仍f0082781575843db3af1d9f228f1e943a0d37fc8951694574b77c25478d324fc，可信本地来源已记录归档后的commit。三个根入口wrapper均通过bash -n；预检逐文件核验固定数据、源码、checkpoint、端口及每卡至少20GiB空闲显存。

## 证据与验收

三个Testing均finished／exit0且独立审计通过，各35,598用户、输出[35598,10,4]，用户完整唯一、SID合法且行内无重复、双writer一致。四指标最大复算误差为3.2959746043559335e-17；Sports NDCG@10三seed mean±sample std为0.014397749002857535±0.0006333649402046876（ddof=1）。Beauty与Sports各三格已完成，完整矩阵6/9。

- training-completion.json：三格50k／500次Validation／finished／exit0、首次最高val选点、checkpoint／Artifact身份和实际配置。
- testing-launch.json：三次实际Testing命令、独立run目录／tmux、GPU、端口和输入身份。
- seed42-testing-audit.json、seed200-testing-audit.json、seed2026-testing-audit.json：正式Testing结束后的零模型forward独立核验。
- three-seed-summary.json：审计通过后从逐seed指标计算四项mean与sample std（ddof=1），绑定输入证据SHA。
- remaining-training-status.json：Toys三格实际训练状态的只读回执。

独立审计复用上一轮已验证的audit_testing.py，检查源码归档字节、训练与Testing的checkpoint/SID lineage、实际缓存checkpoint SHA、固定TFRecord文件、全量用户与标签、keyed预测bundle、SID合法／唯一、双writer一致及四指标与W&B误差不超过1e-12。逐用户CSV及完整材料保留各node1正式run目录，JSON材料留本地；不将单元成功退出等同于审计通过。

本轮仅3次正式Testing，0新增训练格、0训练重试、0调参、0上游重跑。没有产生dry-run或5step临时运行；正式结果与审计保留。
