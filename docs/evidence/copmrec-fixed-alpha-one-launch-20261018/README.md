# CoPMRec 固定 alpha=1 的 node1 启动回执

用户于 2026-10-18 明确授权在 node1 通过 tmux 启动实验，并要求不持续监控。本回执只记录同步、启动及有限启动核验，不代表训练完成。

后续状态：2026-10-18 用户另行授权推理；训练50k及一次正式 Testing 均已完成，独立审计通过，详见[Testing与完成证据](../copmrec-fixed-alpha-one-test-20261018/README.md)。下文保留当时的启动观测。

## 已启动训练

- 实验：[BMX-166](https://linear.app/baymax104/issue/BMX-166/copmrec-v2-增补-固定-alpha1-vs-可学习混合beauty-seed42)，Beauty / seed42 / fixed_alpha_one / 50,000 optimizer updates。
- W&B：[lwtzxzre](https://wandb.ai/baymaxam/GRID/runs/lwtzxzre)。
- tmux：`bmx-166-alpha1-beauty42-20261018-0230`。
- 物理 GPU：1、7；逻辑设备 `[0,1]`；NPROC_PER_NODE=2；MASTER_PORT=29864。
- 提交时间：北京时间 2026-10-18 02:31:28；训练初始化日志时间：02:32:20。
- 远端输出：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-166_train_20261018_0230`。
- 合并 stdout/stderr：上述目录 `console.log`；运行结束后 wrapper 写入 `exit_code`。

实际命令保存在本目录 [launch.sh](launch.sh)，同一内容已写入远端输出目录。wrapper 调用根目录既有 `copmrec_ablation_train.sh`，经统一 `uv run torchrun ... -m src.main` 启动，使用原 `.venv` 与 `UV_NO_SYNC=1`，未修改远端依赖。训练不默认 dry run，也不自动 Testing。

## 核验范围

通过 `./mutagen_sync.ps1 flush` 同步；三个受管 session 均 Watching for changes、无 conflict。核验10个相关代码、配置和根脚本的本地/远端 SHA256 一致；未读取远端 Git 状态作为版本依据。记录见 [preflight.json](preflight.json)。

启动前再次检查物理 GPU 与端口：最初空闲的 GPU2 被其他任务占用，提交断言在启动前拒绝该组合，随后改选仍空闲的1、7；只提交了一次实际训练，未产生重复实验。

02:32:48 的有限启动核验确认 W&B 已创建且 online 同步、记录完整配置、两个 NCCL rank 均注册、两个 CUDA worker 已使用1、7，未见 traceback 或退出码。resolved 配置为 fixed_alpha_one / frozen_1 / alpha=1.0 / 三目标各1 / FP32 / 50k。原始核验记录见 [startup.json](startup.json)；提交回执见 [launch-receipt.json](launch-receipt.json)。

02:33:43 的最终启动核验直接读取 W&B：run state=running，已记录 trainer/global_step=549，train/mixture_alpha=1，train/loss=18.09571075439453（有限）。日志确认 step500 首次 Validation 和 checkpoint 保存已完成；该 checkpoint 不是最终 own-best。记录见 [running-confirmation.json](running-confirmation.json)。核验到此结束。

未等待50k完成，未启动 Testing，未设置持续监控、自动重跑或后续自动任务。已有 Full 对照继续复用 BMX-120。

## 手动查看

```powershell
ssh -t node1 'tmux attach -t bmx-166-alpha1-beauty42-20261018-0230'
```

在 tmux 内按 Ctrl-b 后按 d 可分离会话，训练继续运行。
