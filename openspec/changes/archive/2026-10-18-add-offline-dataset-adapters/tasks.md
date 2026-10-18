## 1. 离线准备模块

- [x] 1.1 实现 Steam/Amazon Adapter、配置与字段校验。
- [x] 1.2 实现 SQLite 唯一邻居 core、重复策略、稳定序列与可逆映射。
- [x] 1.3 实现 gzip Example 分片、回读校验、manifest 及原子发布。

## 2. 用户入口

- [x] 2.1 实现独立数据格式化 CLI、有界 dry-run 和三个 profile。
- [x] 2.2 扩展 LETTER 白名单，提供中文说明。

## 3. 验证与交付

- [x] 3.1 本地测试数据及模型 batch 契约、分片覆盖、配置与脚本，执行 OpenSpec strict。
- [x] 3.2 本地通过后使用 Mutagen 同步，确认三 session 正常且无冲突。
- [x] 3.3 在 node1 对两来源运行有界 dry-run，核对日志和产物边界并归档回执。

## 4. 全量运行发现的文本编码适配

- [x] 4.1 添加严格 UTF-8 解码 helper，仅通过新数据集 embedding override 启用，保持原预处理和模型接口。
- [x] 4.2 验证 Unicode、数组形状、无损失败及 Hydra override，重新同步后使用 tmux 启动 embedding。
