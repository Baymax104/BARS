## Context

BARS 当前 Full 为固定 alpha=0.5、两损失 Untied。旧名称同时承担包名、实验入口、字段标识和历史记录四种用途；checkpoint 在多层继承中按完整字典严格校验。

## Goals / Non-Goals

**Goals:** 源码标识符、类、脚本、Hydra 入口、新运行标识均使用 bars/BARS；旧 checkpoint 无需改写即可严格恢复。

**Non-Goals:** 不改变模型结构、损失、默认 variant、验证选点、推理协议或预算，不重命名实际保存的运行目录和 Artifact。

## Decisions

1. 迁移目录、文件、import 和 Python 标识符；同步配置 defaults、`_target_`、脚本 source/experiment 和测试 fixture 引用，不保留旧包 wrapper。
2. checkpoint 的 copmrec_* 字段及 copmrec-* 协议字符串作为固定序列化格式保留；内部属性改为 bars_version，trace metadata 键仍使用原序列化名。新 task/method/tag 使用 bars。
3. 当前运行指南改为 docs/bars-versions.md；旧指南保留为历史快照，历史结果、证据目录和 OpenSpec archive 字节不变。活动 spec capability ID 保持，正文中的工程符号同步更新。
4. 删除前保存所有已登记变体的小型完整 checkpoint、loss、dense/hybrid 输出与协议；迁移后逐项核对。以结构测试限制新旧名称的保留位置。

## Risks / Trade-offs

- 动态 Hydra 引用遗漏 → 对所有保留 experiment 组合，真实 Bash 参数测试和目标 import 校验。
- 序列化协议被误改 → 迁移前后完整 checkpoint 元数据及模型输出逐项比较，原有拒绝跨协议测试继续运行。
- 历史命令不再指向当前入口 → 历史记录不追改；当前指南提供映射，历史复现使用旧 Git 版本。
