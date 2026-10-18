# 新数据集离线准备

Steam 和 Amazon 2014 Home and Kitchen 通过来源 Adapter 提前转换为现有 TFRecord 契约。准备工具仅做数据格式化，既有训练、推理和分析仍使用 `src/main.py`；模型输入、reader、collate 和 launcher 不变。

## 输入与协议

- 输入为已校验的 `readable/items.jsonl`、`readable/interactions.jsonl`。数据文件保留在 node1，不纳入代码同步。
- Steam 使用 `username/product_id/date`；Amazon 使用 `reviewerID/asin/unixReviewTime`。日期按 UTC 解析，同时间按源行号排序。
- 商品文本仅来自 metadata；Steam 评论 `text`、Amazon `reviewText/summary` 不作为商品内容。Steam 无 title 时使用 app_name。
- 按唯一用户—商品邻居数迭代计算 5-core；保留所有合格节点之间的重复事件。`deduplicate=true` 是显式替代条件，保留最早时间、最小源行的事件，不可混为默认协议。
- 最后两个事件依次留作验证、测试。training 为完整序列去掉最后两项，evaluation 去掉最后一项，testing 保存完整序列。运行时原有 preprocessing 提取标签、截断历史、注入 SID/padding。
- 源字符串 ID 按 BINARY 顺序映射为从0开始的整数 key，映射文件可逆。真实商品0不会被当成数据准备阶段的 padding。
- 商品目录取最终保留事件中的商品并集；包含仅在验证、测试出现的 cold 商品。seen 只统计 training。
- Steam 默认全量且不采样。`steam_stride7.yaml` 在 full core 后按源用户 ID 排序选第7、14……个用户，不重新执行 core，是独立的 LIGER 风格 profile，不宣称逐用户复现论文。

## dry-run

从 GRID 根目录执行。以下命令每份源文件最多读取500,000条对象，在系统临时目录执行同一套准备、gzip Example 写出和回读校验，不发布正式目录：

```bash
uv run --no-sync -m src.data.preparation \
  --config configs/data_preparation/steam_full.yaml \
  --dry-run --max-records 500000 \
  --report data/preparation-receipts/steam-dry-run.json

uv run --no-sync -m src.data.preparation \
  --config configs/data_preparation/home_and_kitchen.yaml \
  --dry-run --max-records 500000 \
  --report data/preparation-receipts/home-kitchen-dry-run.json
```

回执路径必须在源目录、正式输出目录之外且尚不存在；重复运行应选择新路径。dry-run 出现空 core、metadata前缀无法覆盖事件商品、分片数超过样本数量时会明确失败，不自动降低 core、改变采样或伪造成功。必要时可显式增加记录上限，仍需报告实际消耗和 `bounded_dry_run` 范围。

## 完整准备

省略 `--dry-run` 才会执行全量。此操作应在明确授权全量准备后运行：

```bash
uv run --no-sync -m src.data.preparation \
  --config configs/data_preparation/steam_full.yaml
```

支持已声明字段的 `key=value` override；例如 `source_dir="data/steam/readable"`、`output_dir="data/steam/prepared/another-protocol"`。未知字段、空路径、无效数值、嵌套源/输出目录或已有输出会失败。改变处理条件时必须使用匹配的 protocol 和独立输出目录。

## 输出与验证

```text
data/<dataset>/prepared/<protocol>/
├── items/*.tfrecord.gz          # id:int64_list，text:bytes_list
├── training/*.tfrecord.gz       # user_id:int64_list，sequence_data:int64_list
├── evaluation/*.tfrecord.gz
├── testing/*.tfrecord.gz
├── item_mapping.jsonl           # raw_id 与 key
├── user_mapping.jsonl
└── manifest.json
```

准备使用 SQLite 磁盘暂存，只按用户装载单条序列；不创建 embedding 或 SID，不连接 W&B。所有分片通过现有 TFRecordReader 回读，核对内容摘要、行数、用户身份、共同前缀和目录范围。正式输出在同文件系统临时目录完成校验后原子发布；失败不会覆盖原数据或发布半成品。

默认 items 为32分片，各序列 split 为128分片；覆盖配置中预期的2个 rank、item 12 worker、sequence 32 worker。提高运行时 rank/worker 数时需同步提高准备配置中的覆盖约束。分片必须非空，不能依赖现有文件不足时共享列表的行为。

manifest 包含配置、协议、来源字节哈希及 full/prefix 范围、代码哈希、映射哈希、分片哈希、过滤计数、seen/cold 与验证状态。成功的 dry-run 仅证明有界样本上的数据接入，不代表全量数据或正式实验完成。

完整数据准备通过后，将该输出目录作为原有脚本的 `--data-dir`；embedding、量化与 semantic ID 仍沿用现有阶段，显式提供各自上游路径。旧 Beauty/Sports/Toys 数据不会被重写。

## 新数据集 embedding 的文本编码

新数据商品文本使用 UTF-8。现有 embedding 配置的 `convert_bytes_to_string` 使用 NumPy 默认 ASCII 转换，遇到非 ASCII 字符会失败。新数据集运行时须显式选择新增的严格解码函数，不修改既有配置及模型输入接口：

```bash
bash sem_embeds_inference.sh \
  --data-dir data/steam/prepared/full_5core_v1 \
  --devices '[0]' \
  data.preprocessing_functions.4._target_=src.data.components.text_encoding.decode_utf8_features
```

Home and Kitchen 使用相同 override。该函数保留数组形状和未选中特征，非法 UTF-8 明确失败，不通过丢弃字符处理错误。运行时 resolved config 会记录这一选择。
