# BARS Untied M2：训练审计、own-best Testing与剩余队列接续

> 后续进展：用户要求将新完成训练接续Testing，Sports2026、Toys42、Toys200已验收，完整结果升至8/9，Linear对应三项已Done。最新状态见[已完成训练的Testing回执](../bars-untied-m2-test-next-20261019/README.md)；下文保留本轮5/9时点。

用户于2026-10-19要求继续，承接[初次训练提交](../bars-untied-m2-launch-20261019/README.md)。本轮已验收前4格50k训练，各执行一次自身own-best hybrid Testing并完成独立复算；与复用的Beauty42合计，完整结果覆盖为 **5/9**。Sports2026已在GPU0/7开始双卡训练，三格Toys依次等待。当前父项[BMX-185](https://linear.app/baymax104/issue/BMX-185)仍In Progress；186–189 Done，190 In Progress，191–193 Todo。

## 本轮已完成结果

| 任务 | 数据集/seed | own-best | Testing run | R@5 | N@5 | R@10 | N@10 |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| [BMX-186](https://linear.app/baymax104/issue/BMX-186) | beauty/200 | 42500 | [9vnepv70](https://wandb.ai/baymaxam/GRID/runs/9vnepv70) | 0.0529445960 | 0.0378557037 | 0.0743191879 | 0.0447236694 |
| [BMX-187](https://linear.app/baymax104/issue/BMX-187) | beauty/2026 | 43500 | [wgen76v1](https://wandb.ai/baymaxam/GRID/runs/wgen76v1) | 0.0530340294 | 0.0381497679 | 0.0745427715 | 0.0450870470 |
| [BMX-188](https://linear.app/baymax104/issue/BMX-188) | sports/42 | 47000 | [x36rvxfr](https://wandb.ai/baymaxam/GRID/runs/x36rvxfr) | 0.0282881061 | 0.0189168145 | 0.0414910950 | 0.0231715156 |
| [BMX-189](https://linear.app/baymax104/issue/BMX-189) | sports/200 | 46500 | [02jd25ht](https://wandb.ai/baymaxam/GRID/runs/02jd25ht) | 0.0271644474 | 0.0184190940 | 0.0411259059 | 0.0229177339 |

四格均有finished/exit0、50k结束日志和100次非空raw dense Validation，覆盖每500更新到50000；选用各自首次最高val/ndcg@10，不按Testing重选。不可变checkpoint URI/SHA、Artifact digest、双表cold零、source snapshot verified及逐文件源码校验详见[训练审计](training-audit.json)。last.ckpt实际步数独立记录，Testing全部使用已核验的own-best。

Testing在北京时间13:40:06提交；两格Beauty于13:41:51/52结束，两格Sports于13:44:16/14结束。每格单卡FP32，mixture beam20+全部cold、去重后joint catalog logits/stable catalog-row Top10，无历史排除；learned alpha从本臂checkpoint恢复。

完整用户键、真实标签hash、合法唯一Top10、不可变v0预测Artifact与文件摘要全部通过。四指标用逐用户命中和独立tuple-rank两条CPU路径复算，新Untied与W&B summary最大误差4.17e-17。预测URI/SHA和逐格完整来源保存在[Testing审计](testing-audit.json)。

## 与Shared匹配比较

| 数据集/seed | Shared N@10 | Untied相对Shared | Shared−Untied 95%用户CI | 登记 |
| --- | ---: | ---: | --- | --- |
| beauty/200 | 0.0387272932 | +15.4836% | [-0.0074071818, -0.0044888604] | untied_better |
| beauty/2026 | 0.0396543416 | +13.7002% | [-0.0069429318, -0.0039380135] | untied_better |
| sports/42 | 0.0221601474 | +4.5639% | [-0.0019321921, -0.0001295357] | untied_better |
| sports/200 | 0.0221345211 | +3.5384% | [-0.0017291013, 0.0000835230] | uncertain_or_mixed |

用户配对采用PCG64 seed42、2000次、95% pointwise bootstrap，已另按逐次抽样独立重放。方向为Shared−Untied，相对变化分母为Shared。前三格主指标用户区间支持Untied较优；Sports200点估计较高但区间跨零，保留uncertain_or_mixed。该区间只描述固定checkpoint的用户抽样，不描述训练seed不确定性。

## Beauty三seed汇总

Beauty42继续复用g953gzcq/e4a3b038，并零forward重新读取预测核验；新增Beauty200/2026均已真实验收。以下为seed42/200/2026三格原比例均值和样本标准差（ddof=1）。

| 指标 | Untied mean ± sample std | Shared mean ± sample std |
| --- | ---: | ---: |
| recall@5 | 0.0534364799 ± 0.0007758061 | 0.0479512290 ± 0.0002113230 |
| ndcg@5 | 0.0382291335 ± 0.0004187914 | 0.0315417885 ± 0.0004412058 |
| recall@10 | 0.0747514496 ± 0.0005662156 | 0.0722175021 ± 0.0005272023 |
| ndcg@10 | 0.0450933470 ± 0.0003728676 | 0.0393506237 ± 0.0005398785 |

Sports目前只有两个已验收seed，不填写三seed汇总；Toys三格尚无Untied结果。逐格与三seed结构化结果见[零forward统计](zero-forward-results.json)。

## 剩余训练已接续

原GPU1/6被其他用户任务占用，使原两条队列等待。此次只停止精确argv/PID匹配且未写started_at、未产生source snapshot的4个等待wrapper；原status/console/exit记录移入各输出目录initial-gpu-wait。没有中断已执行模型更新，没有模型训练重试；原run ID、seed、训练参数、输出和端口保留。

新队列使用物理GPU0/7，逻辑DDP[0,1]，顺序：

| 任务 | 数据集/seed | 原训练run | 当前session | 状态 |
| --- | --- | --- | --- | --- |
| BMX-190 | sports/2026 | [86odzgh1](https://wandb.ai/baymaxam/GRID/runs/86odzgh1) | `bmx-190-untied-resume-20261019_133841` | running |
| BMX-191 | toys/42 | [39313apw](https://wandb.ai/baymaxam/GRID/runs/39313apw) | `bmx-191-untied-resume-20261019_133841` | queued |
| BMX-192 | toys/200 | [ljlwvdh2](https://wandb.ai/baymaxam/GRID/runs/ljlwvdh2) | `bmx-192-untied-resume-20261019_133841` | queued |
| BMX-193 | toys/2026 | [zurt85mz](https://wandb.ai/baymaxam/GRID/runs/zurt85mz) | `bmx-193-untied-resume-20261019_133841` | queued |

Sports2026于13:44:27在四个Testing均exit0后接续。13:46:23有限启动核验确认[86odzgh1](https://wandb.ai/baymaxam/GRID/runs/86odzgh1)为running，global_step=499，train/loss=18.93000412、SID=6.92786264、catalog=9.55067253、mixture=2.45146704，均有限；GPU0/7真实PID1070896/1070897，NCCL双rank及WORLD_SIZE=2、FP32/global256/seed2026/50k/500步dense Validation/ckpt_path=null均核验通过。来源SHA仍为390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4，320文件快照origin为verified，见[启动核验](resumed-training-startup.json)。

后继只在前驱exit0后取得两张卡的锁；启动前再次验证源码SHA和GPU闲置，异常即停止队列，不自动重试。余4格Testing属于本次接续授权，尚未提交，须先完成各自训练与own-best审计。

## 成本与验证

本M2八格训练预算保持400k：前4格已完成200k，余4格200k接续；初次训练run身份不重建，训练重试0。新增实际Testing为4个计划内run；Beauty42和全部Shared复用，零forward审计没有新增训练或推理。M3成本、结论与已完成事实保持独立。

本轮Mutagen flush成功、三个session Watching for changes；Testing前454个实际Testing分片逐文件SHA与冻结清单一致。8个本次wrapper均通过bash语法和Hydra compose，根入口相关75项测试通过；未改模型、运行配置、依赖或数据，未运行额外smoke。完整编排身份、命令和等待依赖见[continuation.json](continuation.json)，提交回执见[submit.json](submit.json)，身份与预算核验见[final-verification.json](final-verification.json)，Linear写回见[linear-update.json](linear-update.json)。

当前训练查看命令：

```powershell
ssh -t node1 'tmux attach -t bmx-190-untied-resume-20261019_133841'
```

远端批次目录：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_continue_20261019_133841`。训练仍使用原`logs/copmrec_v2/bmx-190_train_20261019_040843`等输出，console.log/status/exit_code均在每格输出内；具体绝对路径见清单。
