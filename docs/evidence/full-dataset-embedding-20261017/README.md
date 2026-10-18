# 全量数据准备与 embedding 生成回执

2026-10-17，用户授权在 node1 全量准备两组数据并通过 tmux 运行 embedding。远端仓库：`/data3/weizhenyu/projects/GRID`。

## 完成结果

| 数据集 | 用户 | 商品 | 最终交互 | training seen / cold | embedding |
| --- | ---: | ---: | ---: | ---: | --- |
| Steam | 281,210 | 11,961 | 3,927,564 | 11,947 / 14 | 11,961 × 1,024 float32 |
| Home and Kitchen | 66,519 | 28,237 | 551,682 | 28,146 / 91 | 28,237 × 1,024 float32 |

两份正式 manifest 的 scope 均为 full，所有源文件均完整读取并记录字节 SHA256，所有分片回读内容与预期行一致。使用唯一邻居迭代 5-core、保留重复事件、按 UTC 时间与源行稳定排序，不子采样。正式数据目录为 `data/<dataset>/prepared/full_5core_v1/`，源数据保留。

## 运行与产物

准备及运行日志：`data/preparation-receipts/full-embedding-20261017_151510/`。实际成功的 tmux 会话保留退出面板：

- `embed_steam_20261017_151510_r2`：物理 GPU 0；W&B [ijm5c76t](https://wandb.ai/baymaxam/GRID/runs/ijm5c76t)，finished。
- `embed_home_and_kitchen_20261017_151510_r2`：物理 GPU 2；W&B [k3led4ud](https://wandb.ai/baymaxam/GRID/runs/k3led4ud)，finished。

通过既有 `sem_embeds_inference.sh` → `torchrun -m src.main experiment=sem_embeds_inference` 执行，使用本地 `flan-t5-large`、最大文本长度128、batch size 8、float32，保持既有聚合方式。resolved config 记录 dataset_name、prepared manifest 路径及 SHA256。运行前 Mutagen flush 成功，三 session 均 Watching for changes，无冲突，未修改虚拟环境。

最终 bundle 相对于远端仓库的位置：

```text
logs/sem_embeds_steam/runs/20261017_151510_r2/wandb_artifact/merged_predictions_tensor.pt
logs/sem_embeds_home_and_kitchen/runs/20261017_151510_r2/wandb_artifact/merged_predictions_tensor.pt
```

对应固定版本引用：

```text
wandb://baymaxam/GRID/sem_embeds_steam-semantic-embedding:v0
wandb://baymaxam/GRID/sem_embeds_home_and_kitchen-semantic-embedding:v0
```

W&B Artifact 状态均为 COMMITTED，内容为指向 node1 上 bundle 的 file reference。向量文件保存在 node1，未复制到本地。

## 编码适配及重试

首次启动因本次操作的 notes 参数分号未正确转义，在 Hydra 解析阶段退出；修正后，Home and Kitchen 的真实文本触发原默认 ASCII 解码的 UnicodeDecodeError。保留失败日志，加入独立 `src/data/components/text_encoding.py` 严格 UTF-8 解码 helper，成功运行仅增加以下 override：

```text
data.preprocessing_functions.4._target_=src.data.components.text_encoding.decode_utf8_features
```

原有解码函数、默认配置、模型及输入接口保持原样。正式数据无需重写。Steam 的等待重试会话在发现同一问题后停止，最终两个实验均使用上述显式解码选择。

## 验证

- 本次定向单测35项通过，涵盖新增 UTF-8 helper、现有 preprocessing 与离线准备模块；Ruff check/format、Hydra compose 与 helper 实例化、OpenSpec strict 通过。
- 两组实验最终退出码0；W&B API 状态均 finished，配置中的 manifest SHA256 与实际文件相符。
- 通过项目共享 `load_model_output(..., field_name="embedding_path")` 读取最终 bundle，验证 keys 恰好覆盖 `0..N-1` 且无重复，向量形状为 `N × 1024`、全有限值、每行范数非零。
- W&B 固定版本 Artifact 的 reference 与实际 bundle 绝对路径相符。文件大小、SHA256、运行命令及完整数据计数见[机器可读回执](completion-validation.json)。

本次完成数据准备和语义向量生成，未启动量化器、SID 或推荐模型训练。
