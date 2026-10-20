# 已完成实现归档与提交（2026-10-20）

## 归档范围

本次按用户指令归档八个任务已全部完成的 OpenSpec 变更，原 proposal、design、tasks 和 delta 完整保存在 `openspec/changes/archive/2026-10-20-<change-id>/`。通过正式 archive 命令合并规范，新增八项 capability，更新既有 `copmrec-v2-formal-surface` 的一项要求；没有使用跳过规范或跳过验证选项。

| 变更 | 完成内容 |
|---|---|
| add-copmrec-untied-residual | 历史／目录独立残差、匹配初始化、优化器及 checkpoint 契约 |
| add-bars-untied-mechanism-study | 双表去直接目录CE、共同零残差等价、固定生成／排序诊断及贡献分析 |
| unify-bars-run-display-naming | BARS 专用显示名／group，保留既有实现与产物身份 |
| add-intrr-ran-core | 作者共享 RAN、STE 与真实前缀监督 |
| add-intrr-recommender | 数据适配、causal backbone、loss、合法 beam 与严格恢复 |
| add-intrr-baseline-entrypoints | TIGER 对齐配置、统一根脚本、dry-run／5step验证与清理 |
| optimize-intrr-validation-encoding | eval 单 batch 历史编码复用及旧路径输出精确等价 |
| track-intrr-validation-rollout | 实现版本记录、训练自然完成后的来源核验与队列交接 |

## 验证与提交边界

归档前八个提案 strict 校验全部通过。IntRR、CoPMRec 变体、机制分析、LIGER 基类、共享 Artifact loader 与相关配置／真实脚本的聚焦回归共 **494 passed**，全部变更 Python 文件 Ruff 检查通过。新增正式规范已补充具体用途；归档后全部 **116项正式 specs strict 校验通过**，当前无活动提案。

提交按 BARS 实现、IntRR 实现、实验文档整理分组，采用中文 Conventional Commits。JSON、CSV、审计脚本和运行日志继续遵守既有 `.gitignore`，保留本地及 node1，不强制纳入 Git；只提交允许跟踪的实现、测试、规范、说明与证据索引。独立 `../research` 仓库的稿件及状态改动不混入 GRID 提交。

## 实现完成与实验完成

BARS Untied 三数据集三 seed 主矩阵9/9、Beauty42机制三组已完成，README与方法入口说明同步到已验收记录。Shared及旧消融继续保留各自来源身份。

IntRR 的五个实现提案均已完成并可归档，但完整推荐矩阵仅Beauty三个seed完成（3/9）；Sports42正在训练，其余五格排队。其余六格原预算、来源守卫、GPU4/5资源配置和Testing授权边界保持。规范归档不将运行中或待执行实验标记完成，不新增运行、训练重试、预算或远端Git操作。
