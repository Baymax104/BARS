# IntRR Beauty seed42 正式训练启动回执

## 授权与状态

用户在完成分模块接入及 node1 dry-run、5 step 验证后明确要求“在 node1 用 tmux 启动实验”。本次于2026-10-19提交一次从头训练，预算为 **1 × 50,000 optimizer steps**。训练已于北京时间 **2026-10-19 02:47:01** 正常结束，W&B 为 `finished`，退出码0，完整500次验证已核对。用户随后要求“intrr已完成训练，继续”，据此使用自身 validation-best 另行执行一次全量 Testing；没有新增训练、其他 seed、网格搜索或调参。最终 Testing 及比较见[正式结果记录](intrr-beauty42-results-20261019.md)。

| 项目 | 本次记录 |
|---|---|
| W&B | [oipt22mb](https://wandb.ai/baymaxam/GRID/runs/oipt22mb) |
| 运行机器与仓库 | `node1:/data3/weizhenyu/projects/GRID` |
| tmux | `intrr-beauty42-20261019_011801-oipt22mb` |
| run directory | `/data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_20261019_011801_oipt22mb` |
| GPU与端口 | GPU 0、1，共享运行；DDP master port `29851` |
| 本次源码快照 SHA256 | `192009b1d3655047c0786d37ab02ed265c1cf9d0a4bb3707702f8d77682f2dc2` |
| 源码归档 SHA256 | `fd0b74bfa8877dfe9ca824f152e6bb087f5c82a8486f0664cd55847f9be6cd6e` |

## 启动健康核验

2026-10-19 **01:20:49（北京时间）** 核验：W&B状态为 `running`，创建时间为当天01:19:34，group为 `paper_main_intrr_beauty`；NCCL双rank完成注册，tmux存活，尚无 `exit_code`。后续GPU进程交叉核验确认rank0 PID2559528、rank1 PID2559529分别位于物理GPU0/1，WORLD_SIZE=2、run ID均一致。源码manifest已核准来源，完整核验保存在远端本次run directory的 `startup-audit.json`。

| 核验对象 | 实际快照 |
|---|---|
| W&B summary | `trainer/global_step=399`；此为SDK读取时刻的日志快照 |
| train/loss | `27.760393142700195` |
| val/loss | `19.28543281555176` |
| val/ndcg@10 | `0.002867511473596096` |
| val/recall@10 | `0.005680754780769348` |
| 后续checkpoint | `checkpoint_epoch=000_step=000500.ckpt`，checkpoint `global_step=500` |
| 优化器与张量 | 全部Adam states的step为500，所有浮点state有限；UID shape为 `[12101,512]` |

以上W&B指标均为有限值。实际W&B config已逐字段核准50k训练、每100步验证、无QA limit flags、Adam、batch128/64、workers32/16、alignment=0.1、beam10和关闭自动Testing。W&B日志399与稍后checkpoint500来自不同读取时点；500步checkpoint仅验证启动与参数更新，不是最终选定的own-best，也不形成推荐质量比较结论。

## 训练完成与最终选点

完整验证步轴为100、200、…、50,000；W&B 的 `trainer/global_step` 以少1的日志轴记录。500次验证中最高 `val/ndcg@10=0.042060092091560364`，首次最大值位于 **step49,400**。最后一次验证的 NDCG@10 为0.04064462333917618，未用于 Testing 选点。

保留 checkpoint 为 `checkpoint_epoch=000_step=049400.ckpt`，194,162,861 bytes，SHA256 `fe124a7270a901a588dd77b1ba9574a6f1b7148a3c423bc9f15b26706155e1cc`。checkpoint 的 `global_step` 与全部 Adam states 的step均为49,400，模型浮点张量均有限；ModelCheckpoint callback 和 W&B `intrr_train-checkpoint:v0` 均记录相同best score和文件身份，Artifact digest为 `7fe31d2b6a96cbd8a42da97c4e99f7ca`。

固定引用为 `wandb://baymaxam/GRID/oipt22mb?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=049400.ckpt`。训练完成审计及完整验证曲线见本地[证据目录](evidence/intrr-beauty42-test-20261019/README.md)，远端训练目录保留同名 `training-completion-audit.json` 和 `validation-history.json`。

## 固定协议

通用参数以用户选定的 TIGER 为参照，正式入口为根目录 `intrr_train.sh`，由 `uv run torchrun ... -m src.main experiment=intrr_train` 执行，不启用 dry-run。

| 项目 | 协议 |
|---|---|
| 数据 | `data/beauty/{training,evaluation,testing}`；本次仅 training 更新、evaluation 选点 |
| SID | keyed bundle 前4列，4层、每层256 codewords；量化类型 `rkmeans` |
| 采样与历史 | TIGER 连续子序列增强，随机最多32条；180个SID slots，最多44件历史商品，仅压缩表示 |
| train loader | batch128/卡、2进程/global batch256；workers32、timeout60、drop_last=true、persistent_workers=true、pin_memory=true |
| validation loader | batch64/卡、workers16、timeout60、drop_last=false、persistent_workers=false、pin_memory=false |
| 文件分配与随机性 | train按原TIGER行/文件shuffle、assign_files_by_size=false；validation不shuffle、assign_files_by_size=true；seed42 |
| 优化 | Adam，lr=0.0005、weight_decay=0.000001，无scheduler，gradient accumulation=1 |
| 训练 | 50,000 optimizer steps、FP32、双进程DDP；每50 step记日志，无sanity validation |
| 选点 | 每100 step验证，按自身最高 `val/ndcg@10` 保存top1，无early stopping |
| 评价 | 原生合法SID beam10；Recall/NDCG@5/@10；全目录，无历史过滤，无cold额外并入或目录重排 |
| Testing边界 | `run_test_after_training=false`；训练没有自动Testing。用户后续“继续”授权后，独立执行batch32、workers8、单进程全量Testing |

上述装配见 `configs/experiment/intrr_train.yaml`、`configs/data/intrr_train.yaml`、`configs/model/intrr.yaml` 及复用的 TIGER trainer/callback/logger；协议一致性由 `tests/test_intrr_config_script.py` 的 compose 深比较约束。

模型内部选择作者公开 commit `806e0f1969ed61a0748902649b335c0ea066de00` 的 UID-only、共享 RAN 和 hard-forward/soft-backward STE；UID512维、模型256维、RAN hidden512、4层causal T5、6 heads、d_kv64、FF1024、dropout0.15。`alignment_weight=0.1` 采用论文及作者 Python 构造函数默认值；作者公开 YAML 的0.0与论文soft组合同STE执行行为的差异已在[实现来源](../src/recommendation/intrr/SOURCE.md)记录，不作为隐藏配置差异。

## 输入与源码来源

- SID：`wandb://baymaxam/GRID/dq77e3wo?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt`；Artifact `rkmeans_inference_beauty-semantic-id:v0`，digest `19ace08283163fbe687287fbacaa3842`。
- 目录：12,101件商品；catalog SHA256 `de657a22f21e47a9b609749b6921c701ff84d455aa71f7623e9d5a5a10adeef8`。
- 三个split各175份源文件，共525份；源字节为 training `417282085`、evaluation `435615164`、testing `496831085`。逐文件hash保存在远端本次run directory的 `preflight.json`，不复制大清单到仓库。
- `dq77e3wo` 的 `rkmeans` 映射与现有正式 TIGER Beauty seed42 一致，来源为 `../research/src/data/baseline-linear-snapshot-20261010.json` 的BMX-34；当前LIGER同SID配置见 `docs/evidence/liger-baseline-restore-20261007/wandb-live-audit.json` 的BMX-133。当前迁移输入身份见 `docs/evidence/copmrec-hybrid-migration-20261018/source-matrix.json`。
- 本地Git工作区为源码可信源。同步交接使用 `mutagen_sync.ps1` 的受管边界；远端Git状态不作为源码版本依据。本次实际输入身份与源码快照由远端preflight记录。

## 结果解释与预算

本次新增比较用于检验IntRR这一近邻机制在采用TIGER通用配置时的相对推荐质量，不改写历史结果，也不重置既有实验预算。

训练本身仅产生validation选点信息。启动时预定的判断为：IntRR较弱可补充BARS相对该近邻方法的质量证据；IntRR更强则如实更新比较及性能主张，保留机制差异；指标混合或差异不明确则报告相应边界。用户后续授权的Testing已独立执行，实际结果与证据边界见[正式结果](intrr-beauty42-results-20261019.md)。结果方向不自动授权额外seed、调参或扩大预算。

## 监测与产物保留

从本地查看tmux输出：

```powershell
ssh node1 "tmux capture-pane -p -t intrr-beauty42-20261019_011801-oipt22mb -S -80"
ssh node1 "tail -n 80 /data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_20261019_011801_oipt22mb/console.log"
```

会话已增加并选中 `log` 窗口，进入后可直接查看滚动日志；训练wrapper位于原窗口。进入node1仓库后可交互查看：

```bash
cd /data3/weizhenyu/projects/GRID
tmux attach -t intrr-beauty42-20261019_011801-oipt22mb
```

wrapper已写入 `wrapper_pid`、`started_at_utc`；训练结束后写入 `exit_code=0` 与 `finished_at_utc=2026-10-18T18:47:01Z`。正式日志为本次run directory下的 `console.log`。源码身份记录、正式日志和checkpoint均保留，W&B记录正式配置与指标。此前接入阶段dry-run/5 step的临时日志、checkpoint、预测及审计目录已清理；该清理要求不适用于本次正式运行产物。
