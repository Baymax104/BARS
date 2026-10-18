## Context

现有 reader 消费 gzip TFRecord Example；商品字段为 id/text，序列字段为 user_id/sequence_data。LIGER 在模型实例化时已读取 training 数据。用户要求提前准备文件，保持主链路及模型输入接口不变。

## Goals / Non-Goals

目标：两个来源 Adapter、可重现的图过滤/留出/映射、分片校验及独立准备工具。非目标：修改 main/launcher、运行模型、生成 embedding/SID、启动完整实验或默认执行全量准备。

## Decisions

- `src.data.preparation` 是仅用于原始数据格式化的独立命令及函数接口。按本次用户要求，它不属于训练/推理/分析的并行入口，不新增 main 模式。
- Adapter 只产出原始商品 ID/商品文本及用户 ID/商品 ID/UTC 时间/源行号。Steam 使用 username，不使用缺失的原生 user_id；Amazon 使用 reviewerID。评论文本不作为商品内容。
- SQLite 暂存事件及唯一边；迭代删除唯一邻居少于 core 的节点。默认保留每条事件；可选去重保留时间最早、源行最小的事件。
- 全量 profile 不采样。独立 Steam stride7 profile 在全量 5-core 后按原始用户 ID 排序、取每第七个用户，不重新执行 core；明确为 LIGER 风格子集，不声明复现其未固定的用户顺序。
- 源 ID 按二进制字符串序排序映射至 0..N-1，时间/源行稳定排序。training=完整序列[:-2]，evaluation=[:-1]，testing=完整序列；不预先截断历史。
- 用既有 tfrecord 包写 Example，经标准库 gzip 固定 mtime 压缩。共享 writer 属于数据文件写出，不是预测 writer callback。
- 配置声明所有路径。准备输出使用独立、不可覆盖的目录；先写同级临时目录，完整回读后原子发布。manifest 标记 sample/full、协议、源/代码/映射/分片哈希、处理计数、seen/cold 统计。
- dry-run 在临时目录中执行相同准备与回读流程，但每份源文件最多读取显式指定的记录数；不创建正式 output_dir、不修改原始文件、不上传 W&B，不代表全量数据通过。
- 至少配置 world_size×workers 个非空分片；样本不足时明确失败而非重复分配。测试可配置较小 core 和 worker 数。

## Risks / Trade-offs

- 有界前缀样本可能没有 5-core → dry-run 明确报告空 core，不能伪造成功；必要时选择较大有界样本，禁止自动降低正式 core。
- 重复 metadata 的 URL 可不同 → 仅比较内容投影；活跃商品内容冲突或缺失内容失败。无 ID metadata 计数后忽略。
- SQLite 磁盘换取内存上界 → 批量写入并在临时工作目录建索引，不修改原始 JSONL。
- 保留 Home and Kitchen 上游 5-core 来源，但仍按本协议校验唯一邻居并固定切分。

## Migration Plan

先新增并本地验证；通过 Mutagen 三 session 同步代码/配置；node1 执行两来源有界 dry-run，留回执。全量准备、embedding/SID、训练另行启动。回退只需不使用新准备工具，旧数据及主链路保持原状。

## Open Questions

无阻塞项。LIGER 风格子集不声称与原论文用户集合完全一致。
