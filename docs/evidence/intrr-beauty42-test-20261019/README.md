# IntRR Beauty／seed42 正式 Testing 证据

本目录记录一次50k训练与一次自身 validation-best 全量 Testing。训练为 `oipt22mb`，Testing为 `hhaubm7t`；用户在训练结束后要求“继续”。没有新增训练、其他seed、其他数据集或调参。结果解读见[正式结果](../../intrr-beauty42-results-20261019.md)，实现协议见[IntRR说明](../../intrr.md)。

## 证据文件

- `training-completion-audit.json`：在线确认训练finished／exit0，完整500次验证与checkpoint／Artifact／Adam states身份核验；保留实际W&B配置。
- `validation-history.json`：全部500次validation的指标，按实际optimizer step选自身最高NDCG@10；SDK日志的`trainer/global_step`比实际step少1。
- `testing-preflight.json`：Testing命令、预算、输入hash、源码来源、checkpoint引用、GPU与loader参数；启动前重新核对525份源文件和源码字节。
- `audit.py`：零模型forward的独立审计；从原始TFRecord读取每用户target，按键匹配预测，复算指标并验证lineage与产物身份。该脚本仅审计既有结果，不是训练或推理入口。
- `testing-audit.json`：正式Testing状态、产物和独立复算结果。
- `baseline-comparison.json`：已保留审计的Beauty／seed42参考值与原始来源，明确BARS Untied为当前主方法、Shared为对照。
- `comparison.json`：通过审计的IntRR正式指标、同seed参考值及按原始精度计算的相对变化；与研究状态和结果表交叉核对。

JSON和逐用户原始材料按项目证据保存规则留在本地，不默认纳入Git。完整预测、源码快照、TFRecord清单、日志与checkpoint保存在node1正式目录，不套用此前接入阶段的临时记录清理要求。

## 远端位置

训练目录：`/data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_20261019_011801_oipt22mb`。

Testing目录：`/data3/weizhenyu/projects/GRID/logs/intrr/beauty_s42_test_20261019_030930_hhaubm7t`；tmux为`intrr-test-beauty42-20261019_030930-hhaubm7t`，启动脚本和console日志均在该目录。W&B保留[训练run](https://wandb.ai/baymaxam/GRID/runs/oipt22mb)与[Testing run](https://wandb.ai/baymaxam/GRID/runs/hhaubm7t)。

## 比较口径

仅比较Beauty／training seed42，各自own-best的全量Testing。IntRR通用参数按用户选择与TIGER对齐，内部参数保留IntRR配置。LIGER和BARS保留各自hybrid推理，LETTER保留其native SID及额外上游训练；不能称全部方法训练与推理完全相同，也不把单seed结果解释为跨seed稳定性或机制因果证据。
