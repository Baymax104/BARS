# Linear M2任务清理回执

2026-10-20，按用户要求检查并清理M2全部issue，包含已完成项。已回读验证通过。

| 处理 | 数量 | 范围 |
| --- | ---: | --- |
| 移入历史记录里程碑 | 10 | BMX-116、BMX-118至121、BMX-15至19；旧Shared训练与dense评价卡 |
| 保留Untied当前主矩阵 | 9 | BMX-185、BMX-186至193；包含Beauty42/BMX-184复用，共9格实测 |
| 保留有效Shared hybrid对照 | 10 | BMX-168、BMX-170至178；标题和当前角色已明确为Shared对照 |

M2由29个issue精简为19个，全部Done；10个旧dense卡移入“历史记录：已替代评价与训练来源”，保留Done、原始描述、run、checkpoint、SHA和父子关系用于追溯。Shared对照继续有效；不依据数值方向或Done状态删除证据。

M2里程碑说明已重写为9/9完成、400k新增训练及8次Testing完成；清除旧“仅Beauty42完成／八格待执行／未授权”状态。M3、IntRR和其他里程碑未改。没有启动实验或删除W&B产物。

[清理前完整快照](before.json)、[变更计划](plan.json)、[逐项写回](updates.json)、[最终回读验证](verification.json)记录本次调整。来源token、Done和父子关系均核验保留；其他issue元数据逐项对照未变。
