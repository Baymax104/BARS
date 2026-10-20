# BARS Untied M2：node1 训练启动回执

> 后续进展：用户于2026-10-19要求继续，前4格训练已完成审计并接续自身own-best Testing，其余4格等待队列改到GPU0/7。最新状态见[续接回执](../bars-untied-m2-continue-20261019/README.md)；下文保留初次提交时点事实。

用户于2026-10-19明确要求按Linear M2，在node1通过tmux启动BARS多数据集、多seed训练。本次恢复[BMX-185](https://linear.app/baymax104/issue/BMX-185)的8格训练；Beauty42继续复用已完成的 `g953gzcq` / `e4a3b038`。2026-10-19 04:13:56（北京时间）已提交8个独立tmux会话，04:16:03有限观察为1格运行、7格等待。本回执不代表50k或完整主矩阵已完成。

## 任务与运行身份

| Linear | 数据集 | seed | W&B run ID | 物理GPU | 04:16启动状态 |
| --- | --- | ---: | --- | --- | --- |
| [BMX-186](https://linear.app/baymax104/issue/BMX-186) | beauty | 200 | `4r4zx78u` | 6,7 | 运行中 |
| [BMX-187](https://linear.app/baymax104/issue/BMX-187) | beauty | 2026 | `oblbespc` | 0,1 | 等待 GPU0/1 |
| [BMX-188](https://linear.app/baymax104/issue/BMX-188) | sports | 42 | `ow9keoti` | 6,7 | 等待前驱 |
| [BMX-189](https://linear.app/baymax104/issue/BMX-189) | sports | 200 | `s5a3wvfq` | 0,1 | 等待前驱 |
| [BMX-190](https://linear.app/baymax104/issue/BMX-190) | sports | 2026 | `86odzgh1` | 6,7 | 等待前驱 |
| [BMX-191](https://linear.app/baymax104/issue/BMX-191) | toys | 42 | `39313apw` | 0,1 | 等待前驱 |
| [BMX-192](https://linear.app/baymax104/issue/BMX-192) | toys | 200 | `ljlwvdh2` | 6,7 | 等待前驱 |
| [BMX-193](https://linear.app/baymax104/issue/BMX-193) | toys | 2026 | `zurt85mz` | 0,1 | 等待前驱 |

等待任务的run ID是预留身份，只有实际开始后才创建对应W&B run。完整session、端口、输出、根脚本命令及前驱关系见[batch.json](batch.json)，每格实际shell见同目录 `bmx-186-launch.sh` 至 `bmx-193-launch.sh`。

两队列为GPU6/7：186→188→190→192；GPU0/1：187→189→191→193。提交时M3任务已占用0/1/2，第一队列立即开始，第二队列每30秒只检查GPU是否释放。每格有独立session/MASTER_PORT/输出，后继只在前驱exit0后取得slot锁；启动前再次核对源码SHA和GPU闲置。前驱失败或源码变化会停止该队列，不自动重试训练。GPU等待日志中的AssertionError表示占用检查尚未通过，实际状态由 `status` 与 `exit_code` 区分。

## 固定协议与预算

使用现有 `copmrec_ablation_train.sh --variant untied_residual`，仍经 `uv run torchrun --nproc_per_node=2 -m src.main` 统一入口。保留现有variant/evidence_phase/group等实现身份，论文角色为BARS当前主方法。scratch、每卡128/global256、FP32、50k updates；SID CE/joint catalog CE/mixture NLL各1、learned alpha、独立历史/目录残差，base LR0.0003、residual LR0.002、wd0.035、warm2500/cosine50000。每500步raw dense Validation、100次事件，按自身首次最高val/ndcg@10选择own-best。训练期间保留dense模式。

本次提交8×50k=400k训练计划预算，既有已完成700k保持，未把计划量登记为已完成。未提交额外smoke、独立Validation、上游重跑、额外seed或Testing。训练结束后的50k/100Validation/exit0/own-best不可变URI与SHA及hybrid Testing另行核验，本次不自动执行Testing。

## 启动核验

- Mutagen `resume`、`flush`成功；grid-src/grid-configs/grid-root-code均Watching for changes，无conflict，继续使用mutagen.yml的一向replica边界。未修改远端Git或依赖环境。
- 320份受管源码与可信本地source origin一致：`390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4`。当前run的source snapshot origin为verified，archive SHA256为 `a5904942332559e7b80a5bda0f9bf9a1321974d1736247ba9a50e818d2f9d374`。
- 三组SID/embedding Artifact digest、catalog与seen-mask均与冻结来源一致；三数据集三split共9组1818文件逐文件path/size/SHA256全一致，0缺失/额外/变更/重复。见[input-comparison.json](input-comparison.json)与[input-preflight.json](input-preflight.json)。
- 8格均通过根脚本实际argv解析、Hydra compose及bash语法检查；相关既有测试124 passed。compose未进入模型forward，未运行真实单步dry-run。
- [4r4zx78u](https://wandb.ai/baymaxam/GRID/runs/4r4zx78u)于04:16:03为running，trainer/global_step=499；train/loss=18.03929901、sid_loss=6.92755604、content_loss=8.85849476、mixture_loss=2.25324845、mixture_alpha=0.50403571，全部有限。console已确认NCCL两rank和物理GPU6/7，step500完成首次Validation并保存checkpoint。实际W&B配置已核对seed200/Untied双表/50k/500步验证/ckpt_path=null。
- Linear父185与186为In Progress；其余7格为Todo，正文记录已提交及具体等待原因，并撤销本次用户已覆盖的旧M3前置阻塞。旧计划作为启动前记录保留；历史Done保持。

## 查看与产物

当前运行session为 `bmx-186-untied-beauty200-20261019_040843`。进入后用Ctrl-b、d分离，任务继续运行。

```powershell
ssh -t node1 'tmux attach -t bmx-186-untied-beauty200-20261019_040843'
```

远端批次目录：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_untied_20261019_040843`。每格输出是 `/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-<编号>_train_20261019_040843`，包含console.log、status、started_at_utc；结束后写exit_code/finished_at_utc。远端批次保留preflight.json、launch-receipt.json、startup-status.json、wandb-startup.json。本地[linear-launch-registration.json](linear-launch-registration.json)保存本次Linear写入及返回值，启动观察保存在本目录对应JSON与stdout文件。
