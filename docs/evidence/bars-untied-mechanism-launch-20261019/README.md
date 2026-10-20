# BARS Untied Beauty42 机制实验启动记录

用户明确要求同步 node1 后用 tmux 启动当前 M3 三组机制实验。三组及B自动续接Test／贡献分析现均 finished／exit0，训练来源与独立逐用户产物验收全部通过。机制链路获得当前Beauty／seed42证据支持，M3阶段完成，见[结果与论文主线](../../bars-untied-mechanism-results-20261019.md)。

| 组别 | Linear | W&B | 资源 | tmux | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| A 冻结预测贡献分析 | [BMX-206](https://linear.app/baymax104/issue/BMX-206) | [84a07f71](https://wandb.ai/baymaxam/GRID/runs/84a07f71) | CPU | `bmx-206-bars-20261019_040701` | finished／exit0，独立验收通过 |
| B Untied 去直接目录 CE | [BMX-207](https://linear.app/baymax104/issue/BMX-207) | [ec98cca4](https://wandb.ai/baymaxam/GRID/runs/ec98cca4) | GPU0、1／DDP2 | `bmx-207-bars-20261019_040701` | 50k／100val完成；自身best Test与贡献分析独立验收通过 |
| C 固定模型生成×排序 2×2 | [BMX-208](https://linear.app/baymax104/issue/BMX-208) | [1241f8aa](https://wandb.ai/baymaxam/GRID/runs/1241f8aa) | GPU2 | `bmx-208-bars-20261019_040701` | finished／exit0，生产精确复现与独立验收通过 |

远端运行目录为 `/data3/weizhenyu/projects/GRID/logs/bars_mechanism/20261019_040701`，各组输出为 `A_formal`／`B_formal`／`C_formal`，日志为同目录 `A_formal.log`／`B_formal.log`／`C_formal.log`。完成后的 tmux 保留退出面板；状态以退出码、W&B 和结构化产物共同判定。

## 同步与启动验证

通过根目录 Mutagen 入口完成 resume、flush、status；`grid-src`、`grid-configs`、`grid-root-code` 均无 conflict 且为 `Watching for changes`。运行端逐字节重算 320 个受管源文件，与本地来源 SHA `390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4` 一致，正式运行各自归档的 origin 均 verified；未读取远端 Git。

Beauty training／evaluation／testing 各175个分片，共525个，逐文件 hash 与冻结来源一致；RKMeans SID `dq77e3wo:v0`、内容 `3jtt9mpa:v5` 的实际 Artifact digest、目录与 seen-mask 匹配。商品12,101＝seen12,068＋cold33。

三组均在独立 tmux 中显式 dry-run，退出码全0，W&B logger 和结果 writer 按统一 dry-run 契约关闭。B 走通双卡一次优化器更新；C 走通冻结 checkpoint 一个诊断 batch；A 仅加载冻结列表和标签。随后正式启动，B 的真实 W&B loss 满足 `SID CE + mixture NLL`，joint catalog CE 权重0、双表、scratch50k／global256／FP32均核验。

证据：[输入与源码](input-preflight.json)、[dry-run命令](dry-launch.json)、[正式命令](formal-launch.json)、[启动验收](startup-audit.json)、[运行 spec](spec.json)。完整每次命令、运行端 wrapper SHA 与来源摘要均可回溯。

## B 训练后的有界续接

同一 B tmux 会话内已完成 [自身 best 审计](posttrain_audit.py) 和 [Test／贡献续接](posttrain.py)：

1. 训练正常 exit0、达到50k；W&B finished且完整100次 raw dense Validation，步数499至49999。
2. 按训练步排序，取首次最高 `val/ndcg@10`，核验自身唯一 best Artifact 的真实不可变版本、文件 MD5／SHA、checkpoint 步数／variant／双表／cold零／训练目标／来源归档。`last.ckpt` 不作为预算证明或选点替代。
3. 自身首次最佳为step49,000，核验checkpoint SHA `075749c79484c0eb002a6801e11dbd25bc7dfddaf0040d717a34d3b7f7009885`后写 [B_ownbest.json](B_ownbest.json)，仅执行一次hybrid Test [0474e89a](https://wandb.ai/baymaxam/GRID/runs/0474e89a)，现finished／exit0。
4. Test exit0并读取真实预测Artifact后，完成CPU配对贡献分析 [3e62b44e](https://wandb.ai/baymaxam/GRID/runs/3e62b44e)，现finished／exit0；真实来源见[B_test-source.json](B_test-source.json)，[独立验收](B-test-result-audit.json)通过。

任一门禁失败即停止后续步骤，无训练／Test自动重试，不切换checkpoint或按Test重选；W&B同步只做有界只读重试。执行配方保存在运行目录，模型及分析仍只调用已同步的根脚本与 `src.main`。后续如源代码摘要变化，续接会停止等待核验。

## A 已完成结果

[独立验收](A-result-audit.json)复核22,363用户与冻结标签、三份来源SHA和原预测、逐用户指标、PCG64 seed42／2000次配对bootstrap，以及贡献守恒。Untied相对共同零残差的NDCG@10绝对差 `+0.00947986083`，相对 `+26.3407%`，95%用户配对区间 `[0.00716641349, 0.01154454015]`；四指标区间均高于零。Untied对Shared四指标区间也均高于零，并复现既有结果。

NDCG@10差分解为新增命中 `+0.02242031090`、丢失命中 `−0.01608543736`、共同命中排名 `+0.00314498729`，精确加和为总差。W&B分析Artifact `bars_untied_beauty_seed42_contributions-analysis:v0` 已发布，8个文件size／MD5均核验并记录SHA256。新旧标签SHA因编码配方不同，审计已用同一keys／完整SID桥接，标签一致。

该结果支持当前Beauty42商品行为适配的质量贡献；直接目录CE和生成／排序作用继续由B／C各自结果判断。用户配对区间不估计训练seed不确定性。

## 预算与状态

本次M3实际完成1×50k＋1次正式Test；A／C各一次分析，另完成新Test预测贡献分析。M3账本为此前700k＋本次50k＝750k，不包含另行授权M2的执行与成本。本次未重复训练／Test，没有追加机制实验或预算，也不启动、暂停或干预M2／IntRR任务。未创建 Git commit。

阶段问题、统计方向与结果判断规则沿用[机制计划](../../bars-untied-mechanism-plan-20261019.md)。[完成运行回读](completion-collection.json)、[结构化结果与决定](mechanism-results.json)、[B独立审计](B-test-result-audit.json)、[C独立审计](C-result-audit.json)均已保存。父项205和子项206／207／208均Done；当前Beauty42保留“商品适配—直接商品监督—同一相关性贯通生成与排序”主线，新增机制实验为0。
