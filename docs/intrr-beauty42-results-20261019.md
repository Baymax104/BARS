# IntRR Beauty／seed42 正式结果

## 结果与范围

本次完成 **1次50,000步scratch训练 + 1次自身validation-best全量Testing**。训练与Testing均为W&B `finished`、退出码0。训练于北京时间2026-10-19 02:47:01完成，Testing于03:10:22完成，覆盖22,363名用户。**独立产物审计通过**，四指标与W&B的最大误差为`3.469446951953614e-17`；以下为正式Testing结果，完整核验见[证据目录](evidence/intrr-beauty42-test-20261019/README.md)的`testing-audit.json`。

| 方法 | Recall@5 | NDCG@5 | Recall@10 | NDCG@10 |
|---|---:|---:|---:|---:|
| TIGER | 0.0354156420 | 0.0228535645 | 0.0543308146 | 0.0289671570 |
| LIGER hybrid | 0.0377409113 | 0.0239996247 | 0.0559406162 | 0.0298674949 |
| **IntRR** | **0.0367571435** | **0.0241653913** | **0.0560300496** | **0.0303633267** |
| LETTER | 0.0393059965 | 0.0256932023 | 0.0600098377 | 0.0323644097 |
| BARS Shared hybrid（保留对照） | 0.0481151903 | 0.0319636834 | 0.0720833520 | 0.0396702363 |
| **BARS Untied hybrid（当前主方法）** | **0.0543308143** | **0.0386819289** | **0.0753923892** | **0.0454693247** |

全部为Beauty／training seed42，各方法自身own-best的正式Testing；比例指标未乘100。参考方法从已有独立审计回读，本轮没有重新运行参考模型或刷新其W&B状态，精确值与来源见`baseline-comparison.json`。

IntRR四项指标均高于TIGER，NDCG@10相对提高4.8198%；与LIGER hybrid相比，Recall@5较低，其余三项略高，NDCG@10相对提高1.6601%。BARS Untied在该单元四项均高于IntRR，NDCG@10相对提高49.7508%。新增近邻基线支持当前主方法在这一格的推荐质量优势；本次没有跨seed估计，也没有单因素隔离或新增机制干预，不能据此将收益归因于共享、残差或某个单独组件。

## 训练、选点与Testing身份

| 项目 | 记录 |
|---|---|
| 训练run | [oipt22mb](https://wandb.ai/baymaxam/GRID/runs/oipt22mb) |
| Testing run | [hhaubm7t](https://wandb.ai/baymaxam/GRID/runs/hhaubm7t) |
| 训练预算 | 50,000 optimizer steps，500次验证，FP32／DDP2，global batch256 |
| 自身最佳 | step49,400，最高validation NDCG@10=0.042060092091560364 |
| 最后一次validation | NDCG@10=0.04064462333917618；Testing没有使用last checkpoint |
| checkpoint | `checkpoint_epoch=000_step=049400.ckpt`，194,162,861 bytes |
| checkpoint SHA256 | `fe124a7270a901a588dd77b1ba9574a6f1b7148a3c423bc9f15b26706155e1cc` |
| checkpoint Artifact | `intrr_train-checkpoint:v0`；digest `7fe31d2b6a96cbd8a42da97c4e99f7ca` |
| SID Artifact | `rkmeans_inference_beauty-semantic-id:v0`，producer `dq77e3wo`；digest `19ace08283163fbe687287fbacaa3842` |
| catalog | 12,101商品；SHA256 `de657a22f21e47a9b609749b6921c701ff84d455aa71f7623e9d5a5a10adeef8` |
| Testing执行 | node1／GPU0／单进程；batch32、workers8、FP32、beam10 |
| 输出Artifact | `intrr_beauty_seed42_inference-recommendation-output:v0`；digest `24942061549e39f805065a44dad9759a` |
| 输出SHA256 | `3b6a0e52f08210c90e4b59a6d7ce9e28ba3cc7f4903e43ad3c0c3acdc1afaa64` |
| tmux | `intrr-test-beauty42-20261019_030930-hhaubm7t` |
| 源码SHA256 | `192009b1d3655047c0786d37ab02ed265c1cf9d0a4bb3707702f8d77682f2dc2`，与训练相同、local-workspace来源verified |

checkpoint固定引用：

```text
wandb://baymaxam/GRID/oipt22mb?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=049400.ckpt
```

Testing从仓库根目录经`intrr_inference.sh`进入`uv run torchrun --nproc_per_node=1 -m src.main experiment=intrr_inference`，由`Trainer.predict`执行。保留W&B Artifact writer并增加公共LocalPickleWriter，完整启动参数见`testing-preflight.json`及远端`launch.sh`；没有dry-run、数据limit或模型配置覆盖。

## 协议与可比性

IntRR通用配置以用户明确选择的TIGER为参照：同一数据划分、RKMeans SID、TIGER连续子序列采样、180 SID slots／最多44历史商品、batch／workers、Adam lr5e-4／wd1e-6、无scheduler、50k预算、每100步validation选点和原生合法SID beam10。内部参数沿用接入冻结配置：UID512、模型256、RAN512、4层causal T5、6heads／d_kv64、FF1024、dropout0.15、temperature1、alignment0.1。作者来源与公开YAML差异保留于[实现说明](intrr.md)和[来源说明](../src/recommendation/intrr/SOURCE.md)。

LIGER与BARS保留各自hybrid候选生成和排序，LETTER使用其native per-seed SID及额外上游训练；本表不声称全部方法具有相同训练配置、上游预算或推理策略。IntRR／TIGER未排除历史商品、未额外并入cold、未做目录重排，保持完整方法原生评价语义。

## 独立核验与产物

启动前执行Mutagen `resume`、`flush`、`status`，三个session均为Watching、无conflict；再次核对525份数据源文件的size和SHA256、源码清单与本地来源、checkpoint SHA256。完整500点验证曲线、callback最佳值、唯一保留checkpoint、所有Adam states的step49,400及checkpoint浮点张量有限性均通过。

Testing的独立审计从原始TFRecord读取`user_id`和`sequence_data[-1]`，固定SID映射为target；按用户键对齐完整SID预测，独立计算Recall与NDCG@5／@10。输出为`[22363,10,4]`，用户集合完整且唯一，非法SID、每行重复SID均为0，两个writer的key与预测逐元素相同。Top5命中822用户，Top10命中1253用户；逐用户标签SHA256为`55e2602110f989565aa6c5fc00bef99107a17d3d11222c06c46874b9df50e016`，与既有Beauty42身份一致。checkpoint／SID的W&B lineage及模型配置一致性核验通过。审计不实例化模型、不执行forward、不调整选点或配置；checkpoint作为CPU数据读取以核验身份。最终结果文件见`testing-audit.json`。

完整预测、逐用户审计、源码归档、checkpoint与正式日志留在node1：

- 训练：`/data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_20261019_011801_oipt22mb`。
- Testing：`/data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_test_20261019_030930_hhaubm7t`。

本轮新增执行成本仅1次Testing；累计IntRR为1×50k训练+1次Testing，0其他seed或数据集、0调参、0重试。既有BARS预算、Untied当前主方法角色及其他8格尚未启动的状态不变。结果方向不自动触发扩大实验。
