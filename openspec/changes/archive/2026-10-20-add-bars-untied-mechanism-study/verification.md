# 实现验收

状态：实现任务9/9完成，OpenSpec strict通过；正式机制实验尚未运行。

## 验证结果

- 模型／恢复／既有配置脚本回归：227项通过，含新双表去目录CE的24项验证。
- 贡献分析与共同零残差多步等价：25项通过。
- 固定Untied生成／排序机制：19项通过。
- 新脚本／Hydra／dry-run及预测SHA与实际Artifact部署身份：32项通过。
- 既有Artifact loader与lineage回归：24项通过。
- 上述互不重叠的测试文件共327项；Ruff check／format、shell语法与参数、YAML唯一键、预算／null run及本地链接检查通过。

机制组件经内存toy checkpoint和预测的实际Hydra实例化复审。CPU设备配置问题已修正并有回归覆盖。正式production复现、真实数据贡献分析和新去CE训练结果不能由CPU测试替代，仍由Linear206–208单独执行验收。

## 交付

- [当前机制计划](../../../docs/bars-untied-mechanism-plan-20261019.md)
- [待执行命令及来源](../../../docs/evidence/bars-untied-mechanism-20261019/README.md)
- [共同零残差复用回执](../../../docs/evidence/bars-untied-mechanism-20261019/no-residual-reuse-audit.json)
- [结构化验收](../../../docs/evidence/bars-untied-mechanism-20261019/verification.json)

Linear父项BMX-205，三个执行子项BMX-206／207／208均Todo；准备项BMX-194 Done。BARS与IntRR未运行扩展矩阵的18个父子任务已Backlog／Low，原Done不改。当前BARS已完成700k，新增机制训练计划50k＋1Test只计一次，未消费。正式训练／Test／真实数据诊断／远端模型forward均0，未提交Git。
