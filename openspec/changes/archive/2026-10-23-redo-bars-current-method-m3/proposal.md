## Why

当前 BARS 已切换到固定 alpha=0.5、SID/Catalog/mixture 权重1/1/0及 hybrid Validation，旧 M3 的 learned-alpha、三损失与 dense 选点来源无法回答当前方法的组件及链路作用。需要在保留历史证据与已耗成本的同时，重新建立匹配实验与 Linear 当前进度。

## What Changes

- 新增 Shared、双侧零残差、去 Catalog CE 三个当前配方消融身份，保留所有旧变体行为与恢复身份。
- 当前机制入口使用固定0.5的 Full，重做生成(.5/0)×排序(catalog/合法decoder路径分数)四臂；生产臂必须精确复现冻结正式预测。
- 当前贡献入口使用显式冻结预测来源，不将旧三损失对照混入当前方法。
- 重建当前 M3 研究计划、预算及 Linear 跟踪；旧结果保留原始身份，不计入新完成覆盖。

## Capabilities

### New Capabilities

- `bars-current-method-m3`: 当前固定半混合、两损失及 hybrid 选点的匹配消融、机制来源与执行边界。

### Modified Capabilities

- `bars-untied-mechanism-study`: 支持当前固定 alpha 的来源，保留历史显式来源的复现能力。

## Impact

影响 CoPMRec ablation、mechanism、对应 Hydra config、根脚本与 CPU 测试；更新 GRID/research 研究记录及 Linear M3。沿用统一入口、共享 Artifact loader/writer，无新增依赖。正式运行、own-best验收、Testing与最终结果分别登记，不以准备完成替代实验完成。
