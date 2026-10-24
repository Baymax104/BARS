## REMOVED Requirements

### Requirement: Prefix allocation prior SHALL use training-only item frequencies
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Decoder SHALL compute sparse prefix training mass
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Allocation SHALL reserve bounded slots inside a model-score shortlist
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Disabled allocation SHALL preserve generation compatibility
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Allocation run identity SHALL be auditable
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

## ADDED Requirements

### Requirement: Retired capability SHALL expose no executable entrypoints

本能力 SHALL 仅保留历史来源索引，SHALL NOT 提供专用源码、Hydra experiment 或根目录脚本；历史复现使用原 Git 版本与冻结输入，当前实验使用正式方法和 BARS 当前 M3 入口。

#### Scenario: Inspect retired capability
- **WHEN** 检查当前仓库的可执行入口
- **THEN** 本能力的旧专用实现与入口不存在，既有历史证据保持原身份
