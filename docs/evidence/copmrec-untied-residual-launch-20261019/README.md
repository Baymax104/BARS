# Shared / Untied 残差对照的 node1 启动回执

用户于2026-10-19明确要求在Linear M3登记对照、同步代码并通过tmux启动实验。本回执记录一次正式训练提交及有限启动核验，训练仍在运行，不代表50k完成或已有最终对照结果。

## 已启动训练

- Linear：[BMX-184](https://linear.app/baymax104/issue/BMX-184/copmrec-v2-增补-shared-vs-untied-历史目录残差beauty-seed42)，项目「CoPMRec 论文」／M3「3. 机制消融」，状态In Progress。
- W&B：[g953gzcq](https://wandb.ai/baymaxam/GRID/runs/g953gzcq)，Beauty／seed42／untied_residual。
- tmux：`bmx-184-untied-beauty42-20261019_001428`。
- 物理GPU：0、1；逻辑设备 `[0,1]`；NPROC_PER_NODE=2；MASTER_PORT=29819。
- 提交时间：北京时间2026-10-19 00:16:46；W&B创建于00:17:34。
- 远端输出：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-184_train_20261019_001428`。
- stdout/stderr：该目录的 `console.log`；wrapper结束时写入 `exit_code`、`finished_at_utc`。

实际命令保存在本目录 [launch.sh](launch.sh)，同内容写入上述远端运行目录。使用现有根脚本，经 `uv run torchrun --nproc_per_node=2 -m src.main` 统一入口执行；沿用原虚拟环境、UV_NO_SYNC=1，没有修改远端依赖、Git或其他任务。固定一次scratch50k、每500步raw dense Validation，按自身首次最高val/NDCG@10选最终own-best；本轮未启动或排队Testing。

## Linear与同步来源

已查重并创建独立M3补充任务，关联BMX-157、166、170；十章说明及project/milestone/team/机制标签读回通过，旧Done任务状态及正文保持。实际启动后仅更新BMX-184为In Progress并写入启动观察，正式Testing指标、配对区间及最终own-best均留空。对应本地登记及读回为 `linear-registration.json`、`linear-launch-submitted.json`、`linear-running-readback.json`。

从本地GRID根目录执行 `./mutagen_sync.ps1 flush` 成功，grid-src/grid-configs/grid-root-code均为One Way Replica、Watching for changes，无conflict；受管边界与mutagen.yml一致，未同步远端Git、数据、环境或重资产。远端实际298份受管源码和本地source origin逐项汇总SHA一致：

```text
ac2db4ddd12d9eb9c4bd0dab2a7949ddf864be2cee200950af881fba78b06446
```

运行归档 `metadata/source_snapshot/manifest.json` 的origin为verified，archive SHA256为 `7f8dd67c4721fa69a1930d18fd284c40c0b0302141450f2fdb0e792fe97dfb80`。本地HEAD为9b7c396且git_dirty=true；新实现的真实身份由上述源码指纹及归档字节确定，未读取远端Git作为版本依据。

## 输入与启动核验

启动前读取并冻结Beauty training/evaluation/testing各175个分片的逐文件SHA256和汇总，记录在 `input-preflight.json`；这是本次实际输入指纹，不冒充旧训练的原始分片清单。SID `dq77e3wo:v0` 和content `3jtt9mpa:v5` 的实际Artifact digest分别与冻结参考 `19ace08283163fbe687287fbacaa3842`、`ab56af975eac589c27eed6094482cbd7`一致。目录、内容及training-seen组合SHA256为 `85502adea36aa3d44a61579f1811179bb8d3943980cf190f089dacbaa7fa22e1`，与既有参考一致；12101商品中12068 seen、33 cold。

运行配置独立核对通过：untied双表、共享内容投影、三目标权重均1、learned alpha、base LR0.0003／残差LR0.002、AdamW wd0.035、warm2500/cosine50000、DDP2/global256/FP32、seed42、ckpt_path=null。group为paper_ablation_copmrec_beauty，notes含BMX-184及Shared训练rmgfscr0／hybrid Test64mjlgze参照。源数据和配置没有切换至其他dataset、seed或变体。

00:17:40的独立运行检查确认NCCL两rank已注册，rank0 PID2347450在GPU0、rank1 PID2347451在GPU1，WORLD_SIZE=2，工作目录为GRID，tmux pane存活且无exit_code或traceback。00:18:22的W&B观察为running、trainer/global_step=399；总loss18.6440544、SID loss6.9291916、catalog loss9.3371000、mixture loss2.3777628、alpha0.50333774，均有限，见 `running-confirmation.json`。

随后对已保存的step1000 checkpoint做一次只读核验，见 `startup-audit.json`：目录和历史表均为 `[12101,128]`，seen权重均已更新、cold非零元素数均为0；两表独立AdamW moments的step均1000。两组initial LR为 `[0.0003,0.002]`，warmup当前LR为 `[0.00012,0.0008]`，双表残差和catalog契约正确。该checkpoint只证明启动后的实际更新与完整状态，不登记为50k结束后的正式own-best。

已完成650k训练成本和hybrid13+1旧闭环保留；本补充只启动一次50k训练，至少1000次更新已有checkpoint佐证，训练未完成。完整训练结束并核验自身首次own-best后，才进行计划内的一次hybrid Testing。Shared Full继续复用；没有自动重跑、额外seed、扫描或持续监控。

## 手动查看

```powershell
ssh -t node1 'tmux attach -t bmx-184-untied-beauty42-20261019_001428'
```

在tmux内按Ctrl-b，再按d，可分离会话并让训练继续运行。研究协议及后续选点/Testing规则见[实验计划](../../../../research/docs/copmrec-v2-untied-residual-plan-20261018.md)。
