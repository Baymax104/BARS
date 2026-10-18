## Why

Steam 与 Home and Kitchen 已具备校验后的 JSONL 原始数据，但现有实验消费的是整数 key 的商品、用户序列 TFRecord。需要提前构建一致的数据产物，保持现有模型输入和主链路不变。

## What Changes

- 在 data 模块增加 Steam、Amazon 2014 来源适配器及共享离线准备流程。
- 按唯一邻居计算迭代 5-core，默认保留重复交互，时间与源行号稳定排序，执行最后两次交互留出。
- 生成可逆整数映射、gzip TFRecord Example 分片及来源/处理 manifest，使用 SQLite 控制内存。
- 增加独立数据准备配置、命令及有界 dry-run；该工具只做数据格式化，不承担训练、推理、分析。
- LETTER 脚本允许新数据集名称；新增契约测试、文档及 node1 验证回执。

## Capabilities

### New Capabilities

- `offline-dataset-preparation`: 来源适配、图过滤、切分、映射、分片、校验、发布及 dry-run。

### Modified Capabilities

无。现有训练、推理、分析入口和运行时数据契约保持不变。按用户明确要求，数据准备作为主链路之前的独立格式化工具，不增加正式 experiment 的运行模式。

## Impact

新增 `src/data/preparation/`、`configs/data_preparation/`、`tests/data/preparation/` 及说明文档；仅扩展 `letter_common.sh` 数据集白名单。不修改 `src/main.py`、launcher、模型、batch、reader、collate，不新增第三方依赖，不启动正式训练或全量数据准备。
