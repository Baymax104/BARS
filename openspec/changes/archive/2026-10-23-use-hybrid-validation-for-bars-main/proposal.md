## Why

用户要求M2按hybrid Validation选点并重新启动；代码当前硬编码dense选点，且既有Beauty42也采用dense。需要让运行、checkpoint来源及主矩阵覆盖与当前论文hybrid协议一致。

## What Changes

- 显式区分训练选点模式，hybrid验证使用现有beam＋全部cold候选、目录评分稳定Top10路径。
- 当前固定alpha=0.5、无mixture loss主变体默认采用hybrid Validation；保留其他变体和旧dense checkpoint的原身份。
- checkpoint严格记录选点模式及候选流程，拒绝跨选点模式误恢复。
- 停止上一批8格dense队列，保留已耗预算和产物；Beauty42也从scratch重训，新9格共450k训练，不自动Testing。
- 更新Linear、启动证据和研究状态。

## Capabilities

### New Capabilities

- `bars-hybrid-validation-selection`: hybrid选点、来源隔离与授权九格重启。

### Modified Capabilities

无；原dense选点与旧checkpoint兼容路径保留。

## Impact

影响CoPMRec scratch协议、主变体component配置、checkpoint元数据、聚焦测试和M2运行编排。训练目标、优化器、冻结上游、统一入口及其他baseline不变，无新增依赖。
