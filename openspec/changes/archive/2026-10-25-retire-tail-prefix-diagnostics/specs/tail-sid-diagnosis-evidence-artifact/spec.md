## REMOVED Requirements

### Requirement: Diagnosis evidence SHALL be written as a stable structured output
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Diagnosis evidence schemas SHALL preserve raw and prioritized meanings
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Harmful-pair output SHALL be deterministic and bounded
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Diagnosis evidence SHALL be publishable as one W&B Artifact
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Diagnosis evidence output SHALL be atomic and fail visibly
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Diagnosis evidence SHALL preserve module ownership and dependency direction
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Tail-SID diagnosis SHALL optionally consume Prefix Trace Artifacts
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Diagnosis SHALL emit stable prefix-survival mechanism evidence
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Mechanism evidence SHALL preserve exploratory and confirmatory boundaries
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Search-ranking diagnosis SHALL extend the existing unified pipeline optionally
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: New analysis evidence SHALL have independently versioned outputs
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

### Requirement: Legacy statistical meanings SHALL not be silently overwritten
**Reason**: 用户要求清理已脱离当前研究范围的 Tail-SID 与 TIGER 前缀诊断链路。
**Migration**: 历史实验使用原 Git 版本及冻结证据；当前方法使用正式训练、推理和 BARS 当前 M3 入口。

## ADDED Requirements

### Requirement: Retired capability SHALL expose no executable entrypoints

本能力 SHALL 仅保留历史来源索引，SHALL NOT 提供专用源码、Hydra experiment 或根目录脚本；历史复现使用原 Git 版本与冻结输入，当前实验使用正式方法和 BARS 当前 M3 入口。

#### Scenario: Inspect retired capability
- **WHEN** 检查当前仓库的可执行入口
- **THEN** 本能力的旧专用实现与入口不存在，既有历史证据保持原身份
