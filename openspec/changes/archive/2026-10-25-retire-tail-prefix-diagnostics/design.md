## Context

当前 research-state.yaml 的 comparison_roster 保留六种方法，current-plan.md 的剩余实验和预算为0。旧 Tail-SID 全批分析 dataset/datamodule 与当前 BARS 贡献分析使用的 FileDataModule 无依赖关系。TIGER 前缀检查用于正式 beam，必须保留。

## Goals / Non-Goals

**Goals:** 完整删除三条过时链路及孤立 helper，保持正式参数和预测语义，消除公共 writer 对旧 schema 的默认依赖。

**Non-Goals:** 不删除数据、checkpoint、logs、W&B Artifact、冻结JSON、历史文档和其他基线；不移除 BARS 历史模型身份兼容；不启动新实验或修改同步配置。

## Decisions

1. 删除专用配置与 import 闭包而非仅隐藏脚本；配置清单和结构测试同时收缩。
2. decoder 删除 tracing 和 allocation，只保留原 disabled 分支的 sort/topk、乘法概率、合法前缀筛选，不修改模型参数初始化顺序。
3. 保留 AuxiliaryTensorWriter，validator 显式必填。LIGER 的两个实际调用点已显式传 validator，避免继续携带 TIGER schema。
4. 保留历史文档和 Git 记录，在当前文档明确退役范围；旧规格以 REMOVED delta 撤销。

## Risks / Trade-offs

- 普通生成和 checkpoint 兼容回归 → 删除前保存小型内存模型的 state 和生成输出，删除后严格恢复并逐项比较。
- 动态 Hydra 引用残留 → 扫描全部目标、组合全部保留 experiment 并运行配置相关单元测试。
- 旧分析不可直接运行 → 从历史 Git 版本复现，原证据和来源身份保留。
