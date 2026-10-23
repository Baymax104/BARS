# IntRR 比较基线

IntRR 基于作者公开实现 `DreamX-Rec/IntRR@806e0f1969ed61a0748902649b335c0ea066de00` 接入当前框架，通用协议由用户明确选择以 TIGER 为参照。核心计算、数据/推荐接入、配置/脚本分别通过三个 OpenSpec 提案实现，未合并为单一提案。

## 模型与来源

商品 compact UID 经512维嵌入和线性投影进入共享 RAN，逐层 STE codeword 求和得到一个商品 token；4层 causal T5Stack 的最后有效 hidden 再进入同一 RAN 预测 SID。推荐 CE 和历史 SID alignment 都逐层求和，alignment 按历史有效位置平均，保留重复商品的频次权重。生成使用原生合法 SID beam，无历史排除、cold 额外并入或目录重排。

内部参数见 `configs/model/intrr.yaml`；当前使用作者公开代码的 hard-forward/soft-backward STE。`alignment_weight=0.1` 采用论文及作者 Python 构造函数默认值，作者公开 YAML 为0.0，该差异明确保留。FF结构、初始化和完整MIT许可见 [来源说明](../src/recommendation/intrr/SOURCE.md)。

## 与 TIGER 一致的通用协议

| 项目 | 当前默认 |
|---|---|
| 输入 | 相同 TFRecord splits、keyed SID bundle前4列、codebook256 |
| 采样 | 完整复用TIGER连续子序列增强，随机最多32条；不更换为作者仓库增强 |
| 历史 | 原180个SID slots，保留相同的最多44历史商品；仅压缩表示 |
| batch/GPU | train128、validation64、inference32 |
| workers | train32、validation16、inference8；persistent/pin等原样继承 |
| 优化器 | Adam，lr=0.0005，weight_decay=0.000001，无scheduler |
| 训练 | 50000 steps、FP32、accumulate1、DDP，默认两进程 |
| 选点 | 每100step验证，自身最高 `val/ndcg@10`，保存top1，训练后不自动Testing |
| 生成与指标 | 合法SID beam10；Recall/NDCG@5/@10；全目录、无历史过滤 |
| 推理 | 默认单进程；公共ModelOutput输出完整SID，沿用TIGER评价与发布callback |

这是一份采用TIGER统一外部协议的IntRR基线，不将作者仓库的320k预算、不同batch/优化器或历史长度混入比较。catalog按原始商品key排序建立compact UID；UID不是原始key，也不是用户ID。目录与结构身份写入checkpoint，输入目录或模型配置不匹配时拒绝恢复。

## 运行方式

所有命令从GRID根目录执行，SID与checkpoint使用明确本地路径或公共 `wandb://` 引用。`--group` 表示SID量化类型；W&B组通过 `--wandb-group` 设置，默认 `intrr`。

```bash
bash intrr_train.sh \
  --data-dir data/beauty \
  --semantic-id-path /path/to/sid_bundle.pt \
  --group rkmeans --seed 42 \
  --notes "IntRR，采用TIGER统一协议" \
  --devices '[0,1]' --master-port 29841
```

```bash
bash intrr_inference.sh \
  --data-dir data/beauty \
  --semantic-id-path /path/to/sid_bundle.pt \
  --group rkmeans --seed 42 \
  --ckpt-path /path/to/own_validation_best.ckpt \
  --notes "IntRR自身validation-best Testing"
```

显式添加 `--dry-run` 才启用统一dry-run；也支持 `--notes="..."`。额外Hydra override放在命令末尾，覆盖默认值。`NPROC_PER_NODE`、`MASTER_PORT`、`DEVICES` 支持环境默认，CLI端口优先；选择单卡训练时同时设置 `NPROC_PER_NODE=1` 与 `--devices '[0]'`。

## 正式实验计划

2026-10-20最终完成九格矩阵：Beauty／Sports／Toys三个数据集、各三个seed的训练与自身best全量Testing均独立验收通过。NDCG@10 mean±sample std依次为0.03092673±0.00060175／0.01439775±0.00063336／0.02902645±0.00055261。累计9训练／450k＋9Testing，剩余运行0；[最终报告](intrr-m4-results-20261020.md)保存完整四指标、逐格来源及验证边界。以下阶段记录保留历史时点。

2026-10-20后续按用户指令完成Sports三seed自身best全量Testing，各35,598用户及独立审计通过；NDCG@10 mean±sample std为0.01439775±0.00063336。Beauty与Sports共6/9格完成；Toys42继续GPU4/5训练，另外两格排队。[Sports三seed报告](intrr-sports-three-seed-results-20261020.md)保存四指标及来源，以下Beauty阶段3/9记录保留原时点。

2026-10-20按用户继续指令完成Beauty200／2026的自身best全量Testing并独立验收，Beauty三seed齐全；NDCG@10 mean±sample std为0.03092673±0.00060175。其余六格曾因全局源码守卫在起训前阻断，经核准仅七份无关BARS配置变化、IntRR依赖不变后恢复，Sports42训练中、其余五格排队；完整矩阵3/9。详见[Beauty三seed报告与恢复状态](intrr-beauty-three-seed-results-20261020.md)。

2026-10-20已完成一次零forward[训练耗时排查](intrr-speed-diagnosis-20261020.md)：当前run后半段显著变慢，主要证据指向GPU0/7上的跨用户计算竞争；原协议下全量验证占比较高，并发现eval路径两次编码历史的既有冗余。本次仅诊断，正式训练与队列配置保持。

后续完整比较计划已登记于Linear M4：[BMX-195](https://linear.app/baymax104/issue/BMX-195)，详见[IntRR M4实验计划](intrr-m4-plan-20261019.md)。矩阵为Beauty／Sports／Toys×seeds42／200／2026；Beauty42复用已完成结果，其余八格Todo，新增计划400k训练更新＋8次自身best Testing，本次登记没有启动实验。

用户随后明确要求在node1用tmux启动训练，剩余八格已恢复并提交GPU0/7串行队列；Beauty200／BMX-197运行，其余七格排队，训练后自动Testing保持关闭。首格200步checkpoint及Adam状态、双rank、W&B配置与源码输入均核验通过，实际运行身份见[2026-10-19启动回执](evidence/intrr-m4-launch-20261019/README.md)。

## 验证与临时产物

2026-10-20已实现[验证历史编码复用](intrr-validation-optimization-20261020.md)：单验证 batch 编码由两次减为一次，CPU 等价回归和协议检查共141项通过。Beauty200以旧版本正常完成50k／500次验证／exit0；01:44:50通过固定来源核验后，七格队列已切换新版本，配置标记 `validation_implementation=history-encoding-reuse-v1`。下一格Beauty2026当前等待GPU0其他用户进程，满足原资源条件后自动继续；Beauty200尚未Testing。交接状态见对应证据目录。

CPU测试覆盖RAN与作者原函数对照、共享监督梯度、历史位置alignment、完整路径枚举beam、严格checkpoint身份，以及与TIGER的样本和配置一致性。配置测试仅compose，不启动完整experiment。

接入验证阶段，node1用于用户授权的dry-run和5step集成检查；检查关闭外部logger和发布，临时覆盖worker/验证频率不改变正式默认。该阶段临时日志、checkpoint、有限预测和审计文件在核验后删除，检查结果不作为正式推荐质量证据。正式实验在用户明确授权后启动，正式日志和checkpoint保留。

2026-10-19接入核验已通过：本地152项聚焦测试、三个提案strict验证；node1完成单卡dry-run、双卡5step、checkpoint恢复及32条有限预测，输出形状为 `[32,10,4]`，候选SID合法且每条无重复。该次临时运行目录、tmux和作者源码审计目录均已清理。

用户随后授权正式启动，训练完成后要求“继续”；Beauty／seed42已完成单次50k训练和自身best全量Testing。训练[oipt22mb](https://wandb.ai/baymaxam/GRID/runs/oipt22mb)的500次验证选step49,400；Testing [hhaubm7t](https://wandb.ai/baymaxam/GRID/runs/hhaubm7t)覆盖22,363用户，独立产物审计通过，R@5=0.03675714350、N@5=0.02416539128、R@10=0.05603004964、N@10=0.03036332669。四指标与W&B最大误差3.5e-17，数据／源码／checkpoint／lineage核准，完整比较与范围见[正式结果](intrr-beauty42-results-20261019.md)及[启动回执](intrr-beauty42-launch-20261019.md)。其他seed和数据集未运行。
