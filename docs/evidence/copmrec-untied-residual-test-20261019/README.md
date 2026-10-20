# Untied 自身 own-best 的 hybrid Testing 回执

用户于2026-10-19确认训练完成并要求继续test。此次仅执行原计划的一次Beauty/seed42单卡hybrid Testing，已finished/exit0；最终W&B指标和预测bundle已产生，Shared／Untied配对统计和独立复算已完成，BMX-184 Done，结果为untied_better。

## 训练完成与选点

训练 [g953gzcq](https://wandb.ai/baymaxam/GRID/runs/g953gzcq) 为finished，exit0，日志确认max_steps=50000。W&B完整history中100次非空Validation事件覆盖每500更新；其global_step从499至49999为零基记录。首次最高val/ndcg@10为0.05917841196060181，对应optimizer step39500。采用本臂own-best，不按Testing重选。

- checkpoint：`wandb://baymaxam/GRID/g953gzcq?role=checkpoint&alias=v0&file=checkpoint_epoch=000_step=039500.ckpt`。
- SHA256：`cb77a0e2e713eef876cf88fb1088c7b6e5fdcb9657416db1b8056944017c576c`。
- W&B checkpoint文件digest与本地文件逐字摘要匹配；两表各[12101,128]、cold非零数各0。
- 三split各175分片，共525个文件SHA256与训练前记录一致。
- 完整审计：[training-completion-audit.json](training-completion-audit.json)。v2已完成训练累计700k，原650k和本次50k分别保留。

## Testing提交

- W&B：[e4a3b038](https://wandb.ai/baymaxam/GRID/runs/e4a3b038)。
- tmux：`bmx-184-untied-test-20261019_022643`。
- 物理GPU7 → 逻辑[0]；NPROC_PER_NODE=1；FP32；沿用远端原环境，不修改依赖。
- 输出：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/bmx-184_test_20261019_022643`；日志为其`console.log`。
- 实际命令：[launch.sh](launch.sh)；运行身份：[launch-spec.json](launch-spec.json)。
- 统一入口经`copmrec_ablation_inference.sh`执行`uv run -m src.main`；标准predict/Testing指标链路。mixture beam20并入全部cold，去重后按joint catalog logits/stable catalog row取Top10，无历史排除，learned alpha由checkpoint恢复。
- Shared比较仍复用`64mjlgze`；没有新增训练、其他seed、独立Validation或扫描。

## 启动前验证

Mutagen flush成功，三个session Watching for changes且无conflict。历史训练归档中的全部源文件逐文件核验无改动；当前额外IntRR文件使整体source SHA更新为`192009b1d3655047c0786d37ab02ed265c1cf9d0a4bb3707702f8d77682f2dc2`，origin为verified。远端Git不作来源依据。根脚本shell语法和实际wrapper Hydra compose通过；相关124项测试通过。

## 查看日志

```powershell
ssh -t node1 'tmux attach -t bmx-184-untied-test-20261019_022643'
```

## 完成核验

实际已恢复step39500模型权重，运行时GPU7进程PID2841858、显存1794MiB；后续结束时GPU7已释放。W&B finished、wrapper exit0，699个predict batch，22363名用户。预测产物已发布为不可变v0；本地bundle形状[22363,10,4]、user key唯一、全部SID属于合法目录、每用户Top10唯一，基本核验通过。

| 指标 | Untied Beauty42 hybrid |
| --- | ---: |
| Recall@5 | 0.05433081429146358 |
| NDCG@5 | 0.038681928901062264 |
| Recall@10 | 0.07539238921432724 |
| NDCG@10 | 0.04546932472217079 |

原表来源为W&B run e4a3b038 summary；后续独立复算已通过，误差小于3.5e-17。预测URI：`wandb://baymaxam/GRID/e4a3b038?role=recommendation_output&alias=v0&file=merged_predictions_tensor.pt`；文件SHA256：`f15c09e0464de7f33eeb9eeabe00f55758f51028d088c923f48b4257ece0ca93`。

[完成回执](running-confirmation.json)、[W&B summary及Artifact元数据](completion-summary.json)、[bundle基本核验](bundle-audit.json)。Shared／Untied用户配对复算及置信区间已完成，BMX-184 Done；本次不新增训练或其他推理。


## Shared／Untied 配对复算结案

| 指标 | Shared | Untied | Shared−Untied | 95%用户配对区间 | Untied相对Shared |
| --- | ---: | ---: | ---: | --- | ---: |
| recall@5 | 0.04811519 | 0.05433081 | -0.00621562 | [-0.00836203, -0.00393507] | +12.9182% |
| ndcg@5 | 0.03196368 | 0.03868193 | -0.00671825 | [-0.00830449, -0.00517737] | +21.0184% |
| recall@10 | 0.07208335 | 0.07539239 | -0.00330904 | [-0.00594732, -0.00062603] | +4.5906% |
| ndcg@10 | 0.03967024 | 0.04546932 | -0.00579909 | [-0.00734550, -0.00432065] | +14.6182% |

PCG64 seed42、2000次、95% pointwise用户bootstrap；同一22363用户及真实标签严格配对。四区间均低于零，按事前规则登记untied_better；单独tuple排名复算与逐次bootstrap重放通过。Shared/Untied总参数为11031809/12580737，增加1548928（14.0406%），两侧cold行均为零。结果不唯一归因容量、共享约束或梯度耦合，不自动更换正式Shared版本或追加实验。

结构化结果：[comparison.json](comparison.json)；[研究结果](../../../../research/docs/copmrec-v2-untied-residual-results-20261019.md)。本轮0次训练、Testing和模型forward；累计700k与原成本保留。
