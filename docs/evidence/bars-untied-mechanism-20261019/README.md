# Untied Beauty42 机制实验准备、提交与验收

代码、配置、CPU验证和Linear安排已完成。用户已明确授权同步 node1 后用 tmux 启动三组机制实验；三组显式 dry-run 均 exit0，正式会话通过来源／配置核验，**A、B、C均已完成且独立验收通过，M3机制阶段完成，追加机制实验与训练预算均为0**。本地最小模型测试及远端 dry-run 不计作正式研究结果。阶段计划见[机制计划](../../bars-untied-mechanism-plan-20261019.md)，结论汇总见[机制结果分析](../../bars-untied-mechanism-results-20261019.md)，实现见[OpenSpec归档](../../../openspec/changes/archive/2026-10-20-add-bars-untied-mechanism-study/proposal.md)。

## 任务与证据

| 任务 | 当前状态 | 正式执行成本 |
| --- | --- | --- |
| [BMX-194](https://linear.app/baymax104/issue/BMX-194) 实现与共同零残差复用审计 | 准备Done；[复用回执](no-residual-reuse-audit.json) | 0新正式run |
| [BMX-206](https://linear.app/baymax104/issue/BMX-206) 冻结预测贡献分析 | `84a07f71`，CPU，finished／exit0，独立验收通过 | 1次CPU Trainer.test分析，0模型forward |
| [BMX-207](https://linear.app/baymax104/issue/BMX-207) Untied去直接目录CE | train `ec98cca4`，50k／100val／first-best49000；Test `0474e89a`与贡献`3e62b44e`均finished／exit0，独立验收通过 | 已完成1×50k＋1自身best Test，另1次零forward贡献分析 |
| [BMX-208](https://linear.app/baymax104/issue/BMX-208) 固定模型生成×排序2×2 | `1241f8aa`，GPU2，finished／exit0，production逐用户精确复现，独立验收通过 | 已完成1次固定checkpoint诊断，两搜索四排序，0训练 |

父项[BMX-205](https://linear.app/baymax104/issue/BMX-205)。本阶段准备时，BARS185/186–193与IntRR195/197–204共18个未完成父子任务移至Backlog／Low、依赖205；已完成任务保持Done。原矩阵各400k＋8Test保留，不计当前50k机制训练预算。之后用户已另行授权并提交M2八格训练，其当前执行状态见[研究执行计划](../../../../research/ideas/current-plan.md)，不从本页历史快照推断。[Linear前快照](linear-before.json)、[准备完成回读快照](linear-after.json)、[实现验收](verification.json)。

## 本次提交与参考命令

本次标签为 `20261019_040701`，来源与资源见[启动 spec](../bars-untied-mechanism-launch-20261019/spec.json)，实际 argv、tmux 和 wrapper 指纹见[正式提交回执](../bars-untied-mechanism-launch-20261019/formal_launch.stdout.txt)。三个正式 tmux 分别为 `bmx-206-bars-20261019_040701`、`bmx-207-bars-20261019_040701`、`bmx-208-bars-20261019_040701`。三组显式 dry-run 已 exit0，正式运行来源与配置核验通过；[A独立验收](../bars-untied-mechanism-launch-20261019/A-result-audit.json)、[B Test及贡献独立验收](../bars-untied-mechanism-launch-20261019/B-test-result-audit.json)、[C独立验收](../bars-untied-mechanism-launch-20261019/C-result-audit.json)均通过。tmux名称保留为执行溯源，不表示会话仍在运行。

以下保留从GRID根目录执行的参考入口，实际本次命令以提交回执为准；不要重复提交同一正式 run。`--dry-run`由统一launcher关闭W&B／结果writer并限制一个batch，不能替代正式结果验收。代码交付沿用Mutagen入口及三个session检查；输入来源见[本次启动核验](../bars-untied-mechanism-launch-20261019/preflight.stdout.txt)。

固定输入：data/beauty，RKMeans SID producer `dq77e3wo`／v0，内容producer `3jtt9mpa`／v5，与已完成Untied来源一致；本次启动核验已重核分片字节、目录、seen-mask及上游指纹。

### A：零模型forward贡献分析

```bash
bash ./bars_untied_mechanism.sh \
  --analysis contributions --dataset beauty --seed 42 --devices 1 \
  --data-dir data/beauty \
  --semantic-id-path 'wandb://baymaxam/GRID/dq77e3wo?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt' \
  --embedding-path 'wandb://baymaxam/GRID/3jtt9mpa?role=semantic_embedding&alias=v5&file=merged_predictions_tensor.pt' \
  --notes 'BMX-206：Untied/Shared/共同零残差；按原身份配对，0模型forward'
```

默认三份预测的不可变URI与SHA在experiment中声明，公共loader核验实际Artifact部署metadata；结果进入W&B分析Artifact和`${paths.output_dir}/analysis`。四指标的差方向为Untied−对照，相对分母为对照。旧no_residual保留原run `gtwv2c4n`／`xzfp1pgt`。

### C：固定checkpoint生成／排序2×2

```bash
bash ./bars_untied_mechanism.sh \
  --analysis generation --dataset beauty --seed 42 --devices '[0]' \
  --data-dir data/beauty \
  --semantic-id-path 'wandb://baymaxam/GRID/dq77e3wo?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt' \
  --embedding-path 'wandb://baymaxam/GRID/3jtt9mpa?role=semantic_embedding&alias=v5&file=merged_predictions_tensor.pt' \
  --checkpoint 'wandb://baymaxam/GRID/g953gzcq?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=039500.ckpt' \
  --checkpoint-sha256 cb77a0e2e713eef876cf88fb1088c7b6e5fdcb9657416db1b8056944017c576c \
  --notes 'BMX-208：固定Untied，两生成四排序；同池含cold，production逐用户复现门禁'
```

四臂为 `learned_catalog`、`learned_decoder`、`alpha0_catalog`、`alpha0_decoder`，另输出 `dense_catalog` 参考。不是alpha扫描，也不将decoder路径评分的teacher forcing等同于候选生成；真实beam coverage独立输出。分块候选评分默认64，可通过 `model.root.candidate_score_batch_size=...` 调整内存，不改搜索预算。

正式结果及[C独立验收](../bars-untied-mechanism-launch-20261019/C-result-audit.json)已通过，production逐用户Top10精确复现。固定catalog的生成N10差为+0.013490634，95%用户区间[0.011630275,0.015288160]；同learned池排序差为+0.016025429，区间[0.014217583,0.017975144]；交互为+0.007999078，区间[0.006005437,0.010024595]。C保留原float32逐用户值及其bootstrap区间，统计描述固定训练来源下的用户抽样；完整预定对比见[结果报告](../../bars-untied-mechanism-results-20261019.md)。

### B：唯一新训练臂

```bash
NPROC_PER_NODE=2 bash ./copmrec_ablation_train.sh \
  --variant untied_no_joint_ce --dataset beauty --seed 42 --devices '[0,1]' \
  --data-dir data/beauty \
  --semantic-id-path 'wandb://baymaxam/GRID/dq77e3wo?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt' \
  --embedding-path 'wandb://baymaxam/GRID/3jtt9mpa?role=semantic_embedding&alias=v5&file=merged_predictions_tensor.pt' \
  --group paper_mechanism_bars_untied_beauty \
  --notes 'BMX-207：双表不变，仅去直接目录CE；50k scratch，自身raw dense best'
```

本次 B 组 wrapper 已完成自动续接：训练 `ec98cca4` 通过[own-best审计](../bars-untied-mechanism-launch-20261019/posttrain_audit.py)的50k／100val／exit0门禁，自身首次最高 `val/ndcg@10` 对应step49000，checkpoint SHA256为 `075749c79484c0eb002a6801e11dbd25bc7dfddaf0040d717a34d3b7f7009885`。随后[续接配方](../bars-untied-mechanism-launch-20261019/posttrain.py)执行唯一一次hybrid Test `0474e89a`，NDCG@10=0.0425214213906603，再执行配对贡献分析 `3e62b44e`；均finished／exit0并通过[独立验收](../bars-untied-mechanism-launch-20261019/B-test-result-audit.json)。Full−noCE N10为+0.00294790333（+6.93275%），95%用户配对区间[0.00183797073,0.00408401294]，四指标区间均正；用户区间不表示训练seed稳健性。下方手动命令保留相同身份接口，不应重复本次已完成的Test。

```bash
bash ./copmrec_ablation_inference.sh \
  --variant untied_no_joint_ce --dataset beauty --seed 42 --devices '[0]' \
  --data-dir data/beauty \
  --semantic-id-path 'wandb://baymaxam/GRID/dq77e3wo?role=semantic_id&alias=v0&file=merged_predictions_tensor.pt' \
  --embedding-path 'wandb://baymaxam/GRID/3jtt9mpa?role=semantic_embedding&alias=v5&file=merged_predictions_tensor.pt' \
  --checkpoint "${NO_CE_OWN_BEST_URI:?先冻结新臂自身best URI}" \
  --checkpoint-sha256 "${NO_CE_OWN_BEST_SHA256:?先核验新臂checkpoint SHA256}" \
  --notes 'BMX-207：新臂自身best正式hybrid Test，不按Test重选'
```

正式部署仍为beam20＋allcold＋目录评分稳定Top10，无历史排除。训练身份沿用原v2 ablation家族协议，新variant与`residual_comparison_protocol`独立登记机制阶段，不重写旧checkpoint。贡献分析 `3e62b44e` 已通过成对新增 `+prediction_paths.untied_no_joint_ce=...`、`+prediction_sha256s.untied_no_joint_ce=...` 接入真实Test预测，bundle SHA256为 `c1226a6c40b849f556395782719e2e4bf8efae28b06c63f09cd7da03926c883d`。四指标、全部用户CSV、命中贡献守恒和2000次PCG64用户配对bootstrap均独立复算一致。

## 验收边界

CPU检查与三组 exit0 的远端 dry-run 验证代码、统计契约和实际启动路径；三组正式会话完成启动核验。A、B、C正式结果均独立验收通过，三组Done，M3机制阶段完成。本阶段已完成1×50k＋一次自身best Test；M3账本此前700k加本阶段50k＝750k，不含另行M2。冻结预测分析与C不增加训练；追加机制实验与训练预算均为0。按原定结果规则保留得到支持的主张。M2后续另行授权提交的训练与IntRR计划保持各自账本、来源及执行状态，不由本页调度；本轮未提交Git。
