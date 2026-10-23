## Context

新版本已完成 Beauty/seed42 的 50k scratch 与自身 best hybrid/dense 测试。运行身份为 untied_fixed_alpha_half_no_mixture，checkpoint 及原始运行配置已独立核验。旧主矩阵为 learned alpha、三损失的九格结果。

## Goals / Non-Goals

Goals：统一当前主方法角色、W&B 分组、当前命令和 M2 进度，保留可追溯历史。

Non-Goals：本轮不新增训练，不修改既有 checkpoint、Artifact、原始指标或论文数值，不将旧机制结果直接改标为新版本结果。

## Decisions

- 继续使用已验收 variant 身份，显示角色由 bars_display 配置登记，不改模型类或 checkpoint 契约。
- 旧 bars_main 的18条记录移入 history，新训练与 hybrid/dense 共3条记录进入 bars_main；新名字去除临时探索标签。
- M2父项和8个未有新版本结果的单元使用 Todo；Beauty42在父项登记已验收复用，不复制创建 issue；Shared 对照保留 Done。
- 当前执行命令使用新变体；旧正文及原始命令在明确历史边界内完整保留。研究状态中旧矩阵与新主矩阵分别记账。

## Risks / Trade-offs

- 历史配置仍含 temporary/evidence_phase 等原始记录 → 当前角色记录由 W&B group、Linear 和研究状态表达，不伪造原始执行条件。
- 旧论文和机制来源与新版本不同 → 标明需后续接入新证据，本次不重编或替换数值。
- broad W&B update 会改写无关字段 → 仅更新 displayName/groupName，并前后核验配置、指标、notes、身份和 Artifact。
