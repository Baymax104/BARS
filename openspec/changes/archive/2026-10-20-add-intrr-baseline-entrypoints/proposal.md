## Why

IntRR核心及推荐接入已分模块实现和验证。现需提供正式baseline入口，将用户确认的TIGER通用协议落实为可compose、可运行的配置与根脚本，并做有界node1集成验证。

## What Changes

- 新增IntRR train/inference薄experiment、模型配置及继承原TIGER流水线的数据配置；trainer/callback/logger直接复用TIGER组件。
- 除已核准的模型内部参数外，对齐TIGER数据/SID、采样、历史信息、batch/worker、Adam/scheduler、50k、val100、ownNDCG10、beam10、全目录无历史排除及输出发布规则。
- 新增根train/inference脚本，支持dry-run、两种notes、checkpoint及额外Hydra override。
- 做配置深比较、脚本语法/quoting/无效参数验证；通过Mutagen同步后在node1运行dry-run及最多5step训练和有限预测验证。
- 验证关闭外部发布，结束后清理本次临时日志、checkpoint、预测产物、tmux和源码审计临时文件；保留提案和使用说明。

## Capabilities

### New Capabilities

- `intrr-baseline-entrypoints`: 继承TIGER通用协议的训练/推理入口、脚本和有界集成验证。

### Modified Capabilities

无。

## Impact

新增IntRR配置、三个根shell脚本、配置/脚本测试及中文使用说明。不修改依赖，不改变现有基线。用户授权仅覆盖dry-run和5step，不启动或排队50k正式实验，不创建提交。
