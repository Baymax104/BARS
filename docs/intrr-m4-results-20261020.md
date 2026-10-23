# IntRR 三数据集三 seed 正式结果

2026-10-20，Beauty／Sports／Toys × seeds42／200／2026 共九格训练、各自validation-best全量Testing及独立验收完成。父项BMX-195与九个实验单元按已验收结果结项。

## 三 seed 汇总

数值为比例，mean ± sample std，三个训练seed，ddof=1。

| 数据集 | R@5 | N@5 | R@10 | N@10 |
|---|---:|---:|---:|---:|
| beauty | 0.03766638 ± 0.00117490 | 0.02494350 ± 0.00071284 | 0.05623873 ± 0.00130932 | 0.03092673 ± 0.00060175 |
| sports | 0.01770699 ± 0.00087820 | 0.01148526 ± 0.00060530 | 0.02673371 ± 0.00106464 | 0.01439775 ± 0.00063336 |
| toys | 0.03597431 ± 0.00095035 | 0.02294362 ± 0.00074701 | 0.05493166 ± 0.00056977 | 0.02902645 ± 0.00055261 |

## 逐格结果与来源

| 数据集 | seed | own-best step | R@5 | N@5 | R@10 | N@10 | Testing run |
|---|---:|---:|---:|---:|---:|---:|---|
| beauty | 42 | 49400 | 0.03675714 | 0.02416539 | 0.05603005 | 0.03036333 | [hhaubm7t](https://wandb.ai/baymaxam/GRID/runs/hhaubm7t) |
| beauty | 200 | 49900 | 0.03724903 | 0.02510006 | 0.05504628 | 0.03085624 | [iyteug3c](https://wandb.ai/baymaxam/GRID/runs/iyteug3c) |
| beauty | 2026 | 47300 | 0.03899298 | 0.02556505 | 0.05763985 | 0.03156061 | [vo7l74h3](https://wandb.ai/baymaxam/GRID/runs/vo7l74h3) |
| sports | 42 | 49700 | 0.01783808 | 0.01148451 | 0.02741727 | 0.01457375 | [jza1eqyq](https://wandb.ai/baymaxam/GRID/runs/jza1eqyq) |
| sports | 200 | 49700 | 0.01677061 | 0.01088034 | 0.02550705 | 0.01369500 | [evhdgof7](https://wandb.ai/baymaxam/GRID/runs/evhdgof7) |
| sports | 2026 | 49400 | 0.01851228 | 0.01209094 | 0.02727681 | 0.01492450 | [alhv8dw4](https://wandb.ai/baymaxam/GRID/runs/alhv8dw4) |
| toys | 42 | 47300 | 0.03621471 | 0.02292788 | 0.05553266 | 0.02914685 | [6pssfdkf](https://wandb.ai/baymaxam/GRID/runs/6pssfdkf) |
| toys | 200 | 47700 | 0.03678137 | 0.02369837 | 0.05486297 | 0.02950894 | [5dc7umim](https://wandb.ai/baymaxam/GRID/runs/5dc7umim) |
| toys | 2026 | 48200 | 0.03492685 | 0.02220461 | 0.05439934 | 0.02842357 | [12ir36lr](https://wandb.ai/baymaxam/GRID/runs/12ir36lr) |

## 协议与独立验收

冻结协议intrr-shared-ran-tiger-v1：TIGER通用训练配置、每格50k及500次Validation，以自身首次最高val/NDCG@10选择不可变checkpoint。单卡FP32、Testing batch32／workers8、合法beam10，全目录且无历史过滤；同一数据集三seed共享冻结RKMeans SID。Beauty／Sports／Toys每格用户数分别为22,363／35,598／19,412。

每格均核准finished／exit0、checkpoint step／SHA／严格contract、SID与checkpoint Artifact lineage，输出为用户完整唯一的keyed Top10，候选SID合法且无重复。独立原始TFRecord按用户键复算R@5、N@5、R@10、N@10，与W&B误差不超过1e-12。本轮Toys最大误差5.21e-17；此前六格重新只读核对W&B状态／指标、checkpoint及预测字节、输出Artifact digest。审计新增模型forward为0。

本轮Toys三格各执行一次正式Testing，未重复训练或调参。全矩阵累计9次训练／450k更新＋9次Testing；新增八格沿用400k授权，Beauty42原50k与原Testing复用。剩余训练、Testing均0，训练重试0；正式数据和产物继续保留。三seed标准差描述各数据集的训练seed变化，用户级分析与跨数据集比较分别处理。

完整九格指标、checkpoint／预测SHA、输出Artifact身份和输入审计摘要来自[final-matrix.json](evidence/intrr-toys-test-20261020/final-matrix.json)，本表直接由该结构化材料生成；[本轮审计索引](evidence/intrr-toys-test-20261020/README.md)说明各文件。
