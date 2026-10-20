# BARS Untied M2：已完成训练的后续Testing与Linear验收

后续状态：最后一格Toys2026已完成训练、own-best Testing及独立验收，M2现为9/9且父子项Done，见[最终结项回执](../bars-untied-m2-final-20261019/README.md)。下文保留本批8/9历史时点。

用户于2026-10-19明确要求“将已完成的训练进行下一步，然后更新linear状态”。本轮为新完成的Sports2026、Toys42、Toys200各执行一次自身own-best hybrid Testing，三格finished/exit0且独立预测验收通过。主矩阵完整结果覆盖从5/9升为 **8/9**；[BMX-190](https://linear.app/baymax104/issue/BMX-190)、[BMX-191](https://linear.app/baymax104/issue/BMX-191)、[BMX-192](https://linear.app/baymax104/issue/BMX-192)已Done，[父项BMX-185](https://linear.app/baymax104/issue/BMX-185)与[BMX-193](https://linear.app/baymax104/issue/BMX-193)保持In Progress。

## 本轮结果

| 任务 | 数据/seed | own-best | Testing run | R@5 | N@5 | R@10 | N@10 |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| [BMX-190](https://linear.app/baymax104/issue/BMX-190) | sports/2026 | 44000 | [u0p3a36m](https://wandb.ai/baymaxam/GRID/runs/u0p3a36m) | 0.0269116242 | 0.0184260033 | 0.0411539974 | 0.0230230427 |
| [BMX-191](https://linear.app/baymax104/issue/BMX-191) | toys/42 | 37000 | [kdrqzc7i](https://wandb.ai/baymaxam/GRID/runs/kdrqzc7i) | 0.0595507933 | 0.0437832811 | 0.0777869359 | 0.0496344730 |
| [BMX-192](https://linear.app/baymax104/issue/BMX-192) | toys/200 | 39500 | [ibwgb7z2](https://wandb.ai/baymaxam/GRID/runs/ibwgb7z2) | 0.0590871626 | 0.0438316220 | 0.0781475376 | 0.0499860062 |

| 数据/seed | Shared N@10 | Untied相对Shared | Shared−Untied 95%用户CI | 登记 |
| --- | ---: | ---: | --- | --- |
| sports/2026 | 0.0229634649 | +0.2594% | [-0.0009787891, 0.0008521953] | uncertain_or_mixed |
| toys/42 | 0.0458075808 | +8.3543% | [-0.0053765501, -0.0022709036] | untied_better |
| toys/200 | 0.0450602166 | +10.9316% | [-0.0064258958, -0.0032870860] | untied_better |

相对变化分母为Shared。配对采用PCG64 seed42、2000次、95% pointwise用户bootstrap，方向Shared−Untied，另以逐次抽样独立重放。两个Toys单元的主指标区间支持Untied较优；Sports2026区间跨零，登记uncertain_or_mixed。用户区间描述固定checkpoint的用户抽样，训练seed变化由下方实际三seed统计单独记录。

## 训练、选点和预测验收

三格均通过finished/exit0、50k结束日志和100次非空raw dense Validation（每500更新，零基history steps499..49999）。首次最高val/ndcg@10选点分别为44000、37000、39500；未使用Testing重选。三组不可变v0 checkpoint URI、完整SHA256、Artifact digest、双表cold零与320份来源快照校验均通过，见[训练审计](training-audit.json)。last.ckpt实际步数单列为观察，Testing均绑定自身已核验own-best。

每格单卡FP32，mixture beam20+全部cold，去重后joint catalog logits/stable catalog-row Top10，无历史排除；learned alpha从checkpoint恢复。三份输出分别覆盖Sports35598用户、Toys19412用户，完整唯一keys及真实标签SHA与冻结数据一致，全部SID合法且每用户Top10不重复。

输出均为不可变v0 model output bundle，checkpoint URI/SHA/Artifact lineage与实际部署配置匹配。四指标经现有helper和独立tuple-rank两条CPU路径复算，对W&B summary最大误差4.86e-17。预测URI、SHA和逐格四指标/用户配对结果见[Testing审计](testing-audit.json)和[零forward统计](zero-forward-results.json)。审计没有新增训练或模型推理。

## Sports三seed汇总

Sports42/200继续复用已完成预测，并在本轮重新只读核验；Sports2026为本轮新增一次Testing。以下为seed42/200/2026原比例均值和样本标准差（ddof=1）。

| 指标 | Untied mean ± sample std | Shared mean ± sample std |
| --- | ---: | ---: |
| recall@5 | 0.0274547259 ± 0.0007327153 | 0.0271176283 ± 0.0010176454 |
| ndcg@5 | 0.0185873039 ± 0.0002853854 | 0.0177530878 ± 0.0005052996 |
| recall@10 | 0.0412569995 ± 0.0002032187 | 0.0416128247 ± 0.0008186787 |
| ndcg@10 | 0.0230374307 ± 0.0001275012 | 0.0224193778 ± 0.0004713675 |

Toys当前只有seed42/200两格已验收，不生成三seed汇总。Beauty三seed已验收结果保持原来源。本轮8/9验收不代表Toys2026已完成。

## 实际执行与资源

三格于北京时间21:26:41提交独立tmux，在物理GPU3串行执行；根入口仍为copmrec_ablation_inference.sh，经uv run -m src.main统一执行。GPU3已有服务进程，启动守卫要求低利用率和至少8GB显存余量；本轮未停止其他进程或训练。

| 任务 | 开始（北京时间） | 结束（北京时间） | exit |
| --- | --- | --- | ---: |
| BMX-190 | 21:26:41 | 21:29:29 | 0 |
| BMX-191 | 21:29:31 | 21:31:18 | 0 |
| BMX-192 | 21:31:22 | 21:33:07 | 0 |

独立CPU审计于21:36:57完成，三份最终结果全通过。实际命令、checkpoint身份、session与输出见[next-testing.json](next-testing.json)及本目录三个bmx-190/191/192-test.sh；[提交回执](submit.json)、[状态快照](status.json)保留原始观察。远端批次目录为`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_test_next_20261019_212510`。

## 最后一格与预算

M2新增8格训练预算保持400k：7格已完成350k，剩Toys2026一格50k仍进行中。新增7次自身own-best Testing已完成；加复用Beauty42，全矩阵8/9已验收。没有新增训练run、模型重试、上游重跑、额外seed或独立Validation。

21:34:05有限核验，[zurt85mz](https://wandb.ai/baymaxam/GRID/runs/zurt85mz)为running，global_step=4999（约5000/50000更新），train/loss=14.48398781，SID/catalog/mixture loss均有限。Toys/seed2026/双表/FP32/global256/50k/500步dense Validation/ckpt_path=null/物理GPU0/7及verified source均通过；wrapper running、无exit_code。见[last-training-status.json](last-training-status.json)。该格完成后仍须核验own-best并执行其计划内一次Testing。

本轮Mutagen flush成功且三session Watching for changes；431个实际Testing分片逐文件SHA与冻结输入一致，三个wrapper及根脚本bash语法/Hydra compose通过。受管源码SHA保持`390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4`，未改运行时源码、依赖或数据。

## 记录

[最终身份与预算验证](final-verification.json)、[Linear最终写回](linear-update.json)与[研究记录验证](research-records-verification.json)记录本轮收尾；[上一轮5/9回执](../bars-untied-m2-continue-20261019/README.md)和[初次启动](../bars-untied-m2-launch-20261019/README.md)保留各自历史时点。M3与其他研究状态保持独立。
