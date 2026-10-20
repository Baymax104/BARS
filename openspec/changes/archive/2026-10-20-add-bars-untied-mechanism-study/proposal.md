## Why

用户决定先以当前 BARS Untied Beauty／seed42 检验论文机制链路，将多数据集、多 seed 主矩阵后移。现有 Shared 消融与 dense／teacher-forced 诊断不能直接充当 Untied hybrid 的匹配机制证据，需要将商品行为适配、直接目录监督和生成／排序中的评分用途逐项对应到可检验对照。

## What Changes

- 新增 `untied_no_joint_ce` 独立训练／恢复身份，保留双残差表、SID CE、mixture NLL 与原部署，仅去掉直接目录 CE。
- 以小型 CPU 多步优化轨迹审计旧 `no_residual` 与 Untied 双侧冻结零的算法等价，复用时保留原 run、checkpoint 与 variant；不伪造新训练。
- 新增通过统一入口与 `Trainer.test` 运行的固定 Untied checkpoint 机制诊断：生成使用 learned mixture 或合法 decoder，最终在同一候选池中使用目录评分或合法 decoder 路径概率，形成预定 2×2 对照；记录真实候选覆盖、最终命中与配对贡献。
- 诊断的 production 对照必须逐用户复现已冻结 Untied hybrid Top10；使用共享 structured writer 保存明细、统计、身份及 keyed bundles。
- 将当前阶段优先级与有限预算登记到 Linear M3 和研究状态，推迟 BARS 与 IntRR 的未运行多数据集／多 seed 矩阵。本轮完成准备与实现，不启动正式训练、Testing 或远端模型 forward。

## Capabilities

### New Capabilities

- `bars-untied-mechanism-study`：Untied 匹配目录监督消融、共同零残差等价审计及固定 checkpoint 生成／排序机制诊断。

### Modified Capabilities

无。保留现有正式模型、Shared 消融及旧 checkpoint 的行为与不可变契约；新能力使用独立配置和身份。

## Impact

涉及 `src/recommendation/copmrec/ablation.py`、新增机制分析模块、组件／experiment 配置、根入口及 CPU 测试。复用当前数据组件、Artifact 解析、`src.main`、`Trainer.test` 与 structured writer；不新增依赖，不修改正式推理的 trace 限制，不切换默认模型，不改写既有结果。研究文档和 Linear 同步阶段问题、计划成本、运行权限与结果判断规则。
