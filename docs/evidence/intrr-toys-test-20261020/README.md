# IntRR Toys Testing 与九格矩阵完成回执

用户在2026-10-20要求将已完成训练进行下一步。Toys三个seed均核准50k、500次Validation、finished／exit0及自身首次最高val/NDCG@10的checkpoint后，各执行一次全量Testing并独立验收。

| seed | training run | own-best step | Testing run | 物理GPU |
|---|---|---:|---|---:|
| 42 | 6ismz9td | 47,300 | 6pssfdkf | 4 |
| 200 | kie5uzi5 | 47,700 | 5dc7umim | 5 |
| 2026 | keeshepi | 48,200 | 12ir36lr | 3 |

## 本轮验收

三个Testing均finished／exit0，各19,412用户、输出[19412,10,4]，用户完整唯一，候选SID合法且行内无重复，双writer一致。原始TFRecord逐用户独立复算四指标，与W&B最大误差5.204170427930421e-17；checkpoint缓存及原文件SHA、严格contract、不可变v0 Artifact和SID lineage、固定源数据、运行源码归档均通过核验。三次Testing沿用原intrr_inference.sh／src.main，在独立tmux单卡FP32执行，batch32、workers8、合法beam10、全目录且无历史过滤，固定Toys SID producer 3dycz43g:v0。

设备预检确认GPU3/4/5空闲显存均超过20GiB，按用户此前允许共享多余显存的授权执行，保持已有服务。首次SSH／Mutagen连接短暂失败后恢复，最终flush成功且三个session均Watching无冲突后才启动正式任务。源码SHA仍为f0082781575843db3af1d9f228f1e943a0d37fc8951694574b77c25478d324fc，来源verified；没有更改模型或训练协议。

## 九格汇总与来源

- `training-completion.json`：Toys三格完整验证、首次best、checkpoint SHA／contract、Artifact digest及实际训练配置。
- `testing-launch.json`：实际入口、run目录、独立tmux、GPU、端口及固定来源。
- `seed42-testing-audit.json`、`seed200-testing-audit.json`、`seed2026-testing-audit.json`：三个零模型forward独立审计报告。
- `prior-six-reuse.json`：此前Beauty、Sports六格的本轮实时复核，核准W&B训练／Testing finished、完整500次验证首次选点、checkpoint与预测文件字节、四指标及输出Artifact digest，不新增模型运行。
- `final-matrix.json`：九格正式数值与来源、三个数据集的三seed mean／sample std（ddof=1），绑定本轮各审计文件SHA256。

[最终结果报告](../../intrr-m4-results-20261020.md)直接消费上述结构化矩阵。Beauty／Sports／Toys各三个seed均完成，完整矩阵9/9；累计9训练／450k更新＋9Testing，剩余训练、Testing均0。原Beauty42训练与Testing复用；新增八格沿用原400k预算，本轮只增加3次正式Testing，0训练重试、0调参或上游重跑。

完整预测、逐用户CSV、源码快照、checkpoint及正式日志保留在各node1 run目录。没有dry-run／5step临时运行，JSON等材料依现有.gitignore保留本地，不强制纳入Git。归档实现提案与本次实验结项分别记录。
