# BARS 固定半半、无 mixture loss：M2 训练启动回执

用户于 2026-10-22 明确要求“启动linear M2训练”。本次执行 [BMX-185](https://linear.app/baymax104/issue/BMX-185) 下的八格训练，复用已验收 Beauty/seed42（BMX-209，`qtyamris` → `3rthtvc4`），不重复运行该格。

## 提交范围与运行身份

2026-10-22 00:44:10（北京时间），八个独立 tmux 已全部提交。它们在 node1 的物理 GPU0/3 上单队列串行运行，逻辑设备为 `[0,1]`。每格独立 run ID、端口、输出目录和 session；排队单元的 ID 是预留身份，实际开始后才创建 W&B run。

| Linear | 数据集 | seed | W&B run ID | MASTER_PORT |
| --- | --- | ---: | --- | ---: |
| BMX-186 | beauty | 200 | `eui0uqas` | 30186 |
| BMX-187 | beauty | 2026 | `8zs6azd0` | 30187 |
| BMX-188 | sports | 42 | `uaoo9n6t` | 30188 |
| BMX-189 | sports | 200 | `rtv4vg71` | 30189 |
| BMX-190 | sports | 2026 | `hh4vhw7k` | 30190 |
| BMX-191 | toys | 42 | `6ahrhesw` | 30191 |
| BMX-192 | toys | 200 | `3ih770cp` | 30192 |
| BMX-193 | toys | 2026 | `lqce3hj3` | 30193 |

启动阶段的状态以 [startup-status.json](startup-status.json) 和 [wandb-startup.json](wandb-startup.json) 的观察时间为准。提交回执不代表完整训练或 Testing 已完成；新主矩阵的已验收覆盖仍为 1/9。

2026-10-22 00:49:23（北京时间）独立W&B读取确认首格 `eui0uqas` 为running、trainer/global_step=1499、train/loss=15.137815475463867、alpha=0.5，全部已读取训练指标有限，实际config完整核对通过。00:48:26的运行日志已确认NCCL双rank、GPU0/3和step500/1000两次成功Validation及checkpoint保存。当前运行源码快照origin=verified，归档SHA256为 `06be4e268c5aca54c8d899071dbd07eae1c2d9906d2c1e7787609fa59bbdf1aa`，实际归档重算通过。GPU快照中的本批两rank各3860MiB；这是当时使用量，不是完整运行峰值。

## 固定协议与预算

入口为 `copmrec_ablation_train.sh --variant untied_fixed_alpha_half_no_mixture --group bars_main`，最终仍使用 `uv run torchrun --nproc_per_node=2 -m src.main`。Untied 双残差、共享内容投影，固定 alpha=0.5，SID CE/Catalog CE/mixture NLL 权重为 1/1/0；cold residual 双侧为零。保留原始 `evidence_phase=ablation` 及配置内的比较协议身份。

每格 scratch 50k updates，FP32、每卡 batch128/global256，AdamW base LR=0.0003、residual LR=0.002、weight decay=0.035、warmup2500/cosine50000、clip1。每500更新做 raw full-catalog dense Validation，按自身首次最高 `val/ndcg@10` 选点，无历史排除。八格授权训练预算共400k；排队预算不计作已完成更新。

本次仅提交训练：`ckpt_path=null`、`run_test_after_training=false`、`num_sanity_val_steps=0`。没有新上游任务、额外 smoke、独立 Validation、调参、额外 seed、模型重试或 Testing。每格训练退出成功只登记 `finished_pending_audit`；后续仍须验收50k、100次Validation及自身own-best不可变URI/SHA后，再按用户授权执行推荐测试。

## Linear 与论文选点协议的差异

本次严格沿用 Linear M2 的 dense Validation 选点。研究计划顶部的论文修订已改为 hybrid Validation 与推荐使用同一候选流程，且明确仅改论文、未修改训练运行配置。本次没有更改该配置或把 dense 选点来源计入论文 hybrid 选点已验收单元；论文可填的对应单元仍为0/9。后续若按论文新选择协议运行，需要单独明确执行范围。

## 启动检查与队列保护

- Mutagen flush 成功；`grid-root-code`、`grid-src`、`grid-configs` 均连接并处于 Watching for changes，无冲突。未读取远端 Git 作为来源，也未修改远端依赖环境。
- 本地与 node1 的323份受管源码相同，SHA256 为 `ed6ad9d62f2b78cfea55a38ac5618ec14271011ed4df743da77059bcd95bb9ed`，来源为可信本地工作树。运行实际快照另在各格输出 `metadata/source_snapshot/` 中保存。
- 三数据集、三split共1818份TFRecord逐文件路径、大小、SHA256与冻结输入相同；六个上游Artifact的版本名/digest、目录身份与seen-mask也全部相同，详见 [preflight.json](preflight.json)。
- 八格均通过实际根脚本参数解析、完整 Hydra compose/resolve 与 shell 语法检查，预检 model forward 为0。新变体的既有聚焦单元测试10项通过，详见 [local-verification.json](local-verification.json)。
- 同批 `flock` 只允许一格执行；后继仅在前驱exit0后继续。源码发生变化或前驱失败会停止后续队列，不自动重试训练。
- 每格启动前连续三次、间隔5秒检查两卡利用率低于10%、各至少24GiB空余显存；资源不足时每30秒等候。GPU3已有约42GiB的sglang常驻服务，本批不终止已有进程。

## 查看任务

首格 session 为 `bmx-186-bars-half-no-mix-beauty200-20261022_003843`：

```powershell
ssh -t node1 'tmux attach -t bmx-186-bars-half-no-mix-beauty200-20261022_003843'
```

使用 Ctrl-b、d 分离后任务继续运行。远端批次目录为 `/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_fixed_half_no_mixture_20261022_003843`；各格输出为 `/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-<编号>_fixed_half_train_20261022_003843`，包含 `console.log`、`status`、开始时间和结束后的 `exit_code`。

完整身份与原样命令见 [batch.json](batch.json)；提交证据见 [launch-receipt.json](launch-receipt.json)。本目录脚本只传递编排与审计数据，不替代 Mutagen 的受管代码同步或统一模型入口。

Linear登记及最终独立回读见 `linear-registration.json` 和 `linear-final-readback.json`；研究计划和 `research-state.yaml` 已登记本次独立授权、运行/排队身份和预算。当前启动验收汇总见 [final-verification.json](final-verification.json)。
