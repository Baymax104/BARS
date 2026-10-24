## Why

当前研究已完成并进入论文维护，早期 Tail-SID 风险分析、TIGER 前缀追踪和候选槽位干预已脱离当前研究范围，却仍挂在统一配置、数据层和正式 decoder 上。按用户要求删除这些过时可执行链路，减少维护面。

## What Changes

- **BREAKING** 删除 tail_sid_diagnosis、tiger_prefix_trace、tiger_prefix_allocation_probe 三条实验链路及专用源码、配置、脚本和测试。
- 删除仅被旧链路使用的数据容器、dataset/datamodule、preprocessing 和 Artifact 读取支持。
- 简化 TIGER 为正式训练及普通受约束 beam 生成，保持参数键和普通生成结果。
- 公共 AuxiliaryTensorWriter 改为显式传入 validator，保留 LIGER 使用。
- 保留六种正式方法、BARS 当前 M3、历史 checkpoint 身份兼容和已有科学证据。

## Capabilities

### New Capabilities

- `retired-tail-prefix-surface`: 约束旧分析面不存在及当前方法行为兼容。

### Modified Capabilities

下列旧能力撤销全部活动要求，具体标题见各 delta spec；历史实现由 Git 与既有归档追溯。

- `tail-sid-resolution-diagnosis`: 撤销旧链路要求。
- `tail-sid-diagnosis-evidence-artifact`: 撤销旧链路要求。
- `tail-static-risk-standardization`: 撤销旧链路要求。
- `tail-search-ranking-decomposition`: 撤销旧链路要求。
- `tail-candidate-allocation-probe-analysis`: 撤销旧链路要求。
- `tiger-prefix-trace-artifact`: 撤销旧链路要求。
- `tiger-prefix-survival-tracing`: 撤销旧链路要求。
- `tiger-prefix-balanced-allocation`: 撤销旧链路要求。

## Impact

涉及 src/data、src/recommendation/tiger、src/quantization/tail_sid_diagnosis、公共 writer 与对应配置、根脚本、测试、README。无依赖变更，不运行训练或真实推理，不操作实验产物或外部记录。
