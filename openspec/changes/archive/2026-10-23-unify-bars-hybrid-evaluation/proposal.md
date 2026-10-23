## Why

用户明确要求删除W&B全部BARS dense测试记录，后续不区分hybrid/dense，统一默认hybrid。当前显示模板、启动参数和Linear当前引用仍暴露两类测试，需要统一。

## What Changes

- 删除17条经实际部署配置确认的BARS dense测试run，保留独立Artifact及运行快照。
- 保留的BARS run显示名称去掉hybrid分类；其他方法不变。
- BARS测试显示使用test/validation，公共脚本默认hybrid并拒绝dense测试参数；保留原训练全目录验证和内部分析能力。
- 同步Linear当前说明/命令、Run Registry和当前研究状态；历史实际命令与结果带历史边界保留。

## Capabilities

### New Capabilities

- `bars-canonical-evaluation`: 唯一对外推荐测试、记录清理和显示规则。

### Modified Capabilities

无。

## Impact

BARS inference显示配置、公共脚本、相关测试、W&B记录及Linear当前说明。不修改训练损失、checkpoint、上游数据或论文结果，不启动训练或测试。
