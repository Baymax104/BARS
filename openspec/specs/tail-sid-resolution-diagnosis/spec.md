# tail-sid-resolution-diagnosis Specification

## Purpose
本能力已于2026-10-25退役；保留历史身份并禁止恢复专用可执行入口。撤销的原要求与迁移说明见 `openspec/changes/archive/2026-10-25-retire-tail-prefix-diagnostics/specs/tail-sid-resolution-diagnosis/spec.md`。
## Requirements
### Requirement: Retired capability SHALL expose no executable entrypoints

本能力 SHALL 仅保留历史来源索引，SHALL NOT 提供专用源码、Hydra experiment 或根目录脚本；历史复现使用原 Git 版本与冻结输入，当前实验使用正式方法和 BARS 当前 M3 入口。

#### Scenario: Inspect retired capability
- **WHEN** 检查当前仓库的可执行入口
- **THEN** 本能力的旧专用实现与入口不存在，既有历史证据保持原身份
