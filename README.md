# GRID

GRID 是利用商品内容开展生成式推荐研究的实验代码库，基于 PyTorch、Lightning 和 Hydra，将语义向量生成、量化、semantic ID（SID）生成、推荐训练、推理与诊断接入统一入口。

当前可运行的推荐方法包括 **TIGER、LIGER、BARS（CoPMRec）、LETTER、SASRec 和 IntRR**。LIGER 等内容生成式推荐方法是主要比较对象；TIGER 同时提供基础架构与基础对照，SASRec 提供序列推荐对照。各方法在本仓库中的实现与协议以配置、脚本和对应说明为准。

## 环境与安装

- Python：`>=3.11,<3.12`，依赖通过 `uv.lock` 固定。
- 本地开发可使用 Windows / PowerShell；根目录 `.sh` 脚本需要 Bash，GPU 实验通常在 Linux 运行环境执行。
- 数据、预训练模型、checkpoint 与实验产物需要单独准备；安装依赖不会生成这些输入。

从仓库根目录安装环境：

```powershell
uv sync --locked
```

所有命令均从仓库根目录执行。使用 W&B logger 前需配置相应账号与凭据；项目、分组和实验说明通过 `logger.wandb.project`、`logger.wandb.group`、`logger.wandb.notes` 设置。

W&B 默认按研究角色分组：主实验使用 `{method}_main`（如 `bars_main`、`intrr_main`），消融使用 `ablation_main`，机制分析使用 `mechanism_main`。显示名区分方法、数据集、seed、变体和阶段；BARS 使用 `bars` 显示前缀，内部 `copmrec` 入口、checkpoint 和 Artifact 身份保持。旧 learned-alpha 主变体归入 `history`。显式显示组参数及尾随 Hydra override 可覆盖默认显示值，配置规则见 `configs/logger/bars_display.yaml`。

## 目录与配置

| 路径 | 职责 |
| --- | --- |
| `src/main.py` | 统一训练、推理与分析入口 |
| `src/embedding/`、`src/quantization/`、`src/recommendation/` | 各阶段的领域实现 |
| `src/data/` | 数据、dataset / datamodule 与产物读取 |
| `src/common/` | 共享 writer、callback、loss 与 scheduler |
| `configs/experiment/` | 实验入口与组件装配 |
| `configs/` 中的其他组件目录 | 模型、数据、trainer、logger 等具体参数 |
| 根目录 `*.sh` | 各实验的运行脚本与参数解析 |
| `tests/` | 不依赖真实数据、外部服务或 GPU 的单元测试 |
| `openspec/specs/`、`openspec/changes/` | 当前规格、进行中的变更与已完成变更归档 |
| `docs/` | 实现说明、验证记录、历史总结与证据索引 |

Experiment 保持薄入口职责，最终行为由其 `defaults` 组合出的组件配置决定。数据目录、SID、语义向量和 checkpoint 均通过配置传入，不能仅凭旧文档中的目录或命令判断当前行为。

## 实验链路与入口

| 阶段 | 主要 experiment / 根目录脚本 |
| --- | --- |
| 商品语义向量生成 | `sem_embeds_inference` |
| 量化器训练 | `rqvae_train`、`rvq_train`、`rkmeans_train` |
| SID 生成 | `rqvae_inference`、`rvq_inference`、`rkmeans_inference` |
| 推荐训练与推理 | `tiger_train/inference`、`liger_train/inference`、`copmrec_train/inference`、`letter_train/inference`、`sasrec_train/inference`、`intrr_train/inference` |
| LETTER 前置链路 | `letter_cf_train` → `letter_cf_export` → `letter_tokenizer_train` → `letter_sid` |
| 诊断分析 | `tail_sid_diagnosis`、`tiger_prefix_trace`、`tiger_prefix_allocation_probe`、`copmrec_diagnosis` |
| CoPMRec 消融 | `copmrec_ablation_train`、`copmrec_ablation_inference` |
| BARS Untied机制与贡献 | `bars_untied_contributions`、`bars_untied_mechanism`；共用 `bars_untied_mechanism.sh`，通过 `--analysis contributions` 或 `--analysis generation` 选择 |

表中每个名称对应 `configs/experiment/<名称>.yaml`；BARS机制两项共用上述脚本，其他名称对应根目录 `<名称>.sh`，推荐训练和推理名称分别展开为 `_train` 与 `_inference`。LETTER 的前置链路具有独立输入契约，详见 [LETTER 实现](docs/letter.md)。

统一入口通过 `experiment=<名称>` 选择实验。先查看组合配置，无需加载真实数据或启动训练：

```powershell
uv run -m src.main experiment=copmrec_train --cfg job
```

单进程使用 `uv run -m src.main experiment=<名称> ...`；多进程使用 `uv run torchrun --nproc_per_node=<N> -m src.main experiment=<名称> ...`。日常运行优先使用根目录脚本，让脚本完成参数校验与 Hydra 参数装配。

训练与 diagnosis 脚本支持 `--dry-run`，并将其交给统一入口执行最小流程；它仍需有效数据和上游产物。查看配置使用 `--cfg job`。脚本支持 `--notes="..."` 和 `--notes "..."`，末尾追加的 Hydra override 可以覆盖默认值。不同方法的参数名称可能不同，请对照对应脚本。

## BARS（CoPMRec v2）运行示例

当前主方法为 **BARS Untied，固定 alpha=0.5、移除 mixture NLL**，变体身份为 `untied_fixed_alpha_half_no_mixture`。历史侧和目录侧分别学习商品 residual，内容投影共享，SID CE／Catalog CE／mixture NLL 权重为 1/1/0。训练从头初始化，双 GPU、FP32、50,000 次 optimizer update；每500步使用 hybrid Validation，按自身首次最高 `val/ndcg@10` 选择 own-best，训练结束后不自动执行 Testing。

验证和推荐共用混合概率 beam20、全部 cold 商品并集、目录 logits 稳定 Top10，不排除历史商品。公共推理脚本默认 hybrid，并拒绝 dense 部署；显示阶段为 `test` 或 `validation`。

据已保存的独立验收回执，[当前 M2 主矩阵](docs/bars-hybrid-m2-results-20261023.md)覆盖 Beauty／Sports／Toys × seed42／200／2026 共9/9格。[当前 Beauty42 M3](docs/bars-current-method-m3-results-20261023.md)的三个匹配消融、生成／排序机制及冻结预测贡献分析均已验收。IntRR 的[九格基线矩阵](docs/intrr-m4-results-20261020.md)也已完成。实验状态与预算仍由相邻 research 仓库管理；本页引用已有验收，不授权新增运行。

旧 `untied_residual` 的 learned-alpha／三损失矩阵与旧 Shared 结果保留历史来源。裸 `copmrec_train/inference.sh` 使用历史 Shared 配方；当前匹配 Shared 消融需要明确指定 `shared_fixed_alpha_half_no_mixture`，不能直接复用旧配方。

以下 Bash 示例中的路径仅展示参数形式，需替换为实际数据、对齐后的 SID 和商品语义向量。运行脚本前先安装锁定环境；脚本默认设置 `UV_NO_SYNC=1`。

```bash
CUDA_VISIBLE_DEVICES=0,1 NPROC_PER_NODE=2 bash copmrec_ablation_train.sh \
  --variant untied_fixed_alpha_half_no_mixture \
  --data-dir data/beauty \
  --dataset beauty \
  --semantic-id-path logs/inputs/beauty/semantic_ids.pt \
  --embedding-path logs/inputs/beauty/content_embeddings.pt \
  --devices '[0,1]' \
  --seed 42 \
  --master-port 29730 \
  --notes "BARS Untied; fixed alpha=0.5; no mixture NLL; Beauty; seed=42"
```

`CUDA_VISIBLE_DEVICES=0,1` 选择物理 GPU，`--devices '[0,1]'` 使用其映射后的逻辑编号。正式训练脚本要求两个进程，并拒绝通过 checkpoint 恢复训练。

独立推理固定该方法、数据集和 seed 对应的自身最佳 checkpoint，要求单进程及明确的 SHA256。先将 `CHECKPOINT_PATH` 和 `CHECKPOINT_SHA256` 设置为经过核验的路径与 64 位小写十六进制哈希，再执行：

```bash
CUDA_VISIBLE_DEVICES=0 NPROC_PER_NODE=1 bash copmrec_ablation_inference.sh \
  --variant untied_fixed_alpha_half_no_mixture \
  --deployment hybrid \
  --data-dir data/beauty \
  --dataset beauty \
  --semantic-id-path logs/inputs/beauty/semantic_ids.pt \
  --embedding-path logs/inputs/beauty/content_embeddings.pt \
  --devices '[0]' \
  --seed 42 \
  --checkpoint "$CHECKPOINT_PATH" \
  --checkpoint-sha256 "$CHECKPOINT_SHA256" \
  --split testing \
  --notes "BARS Untied; own-best; hybrid Testing"
```

`--split validation` 对应 `evaluation` 数据目录，`--split testing` 对应 `testing`。当前三个匹配消融使用同一 ablation 入口，变体分别为 `shared_fixed_alpha_half_no_mixture`、`no_residual_fixed_alpha_half_no_mixture`、`untied_fixed_alpha_half_no_joint_ce_no_mixture`，协议为 `bars-fixed-half-hybrid-m3-20261023-v1`。每臂只消费自身 own-best checkpoint；旧 dense 选点来源与当前 hybrid 来源不能混用。

机制与贡献共用 `bars_untied_mechanism.sh`：`--analysis generation` 固定当前 Full 做生成／排序干预，`--analysis contributions` 读取明确 URI／SHA 的匹配预测做零 forward 分析。历史来源需显式选择。输入与证据范围见 [BARS 方法与运行入口](docs/copmrec-versions.md)。

## 数据、产物与来源追溯

- 上下游通过 `embedding_path`、`semantic_id_path`、`ckpt_path` 等明确字段衔接；训练、验证、测试及商品级输入目录由 data config 声明。
- Model output bundle 使用 `{"keys": ..., "predictions": ...}`，读取时需保持 key 对齐，不能假设文件内容是裸 tensor。共享本地 writer 的默认合并文件名为 `merged_predictions_tensor.pt`。
- 产物读取集中在 `src/data/components/artifacts.py`，W&B URI 解析在 `src/utils/wandb.py`；输出写入集中在 `src/common/writers/`。W&B 中的文件引用需要对应存储路径在运行环境可访问。
- 可再生成的特征、候选等缓存默认留在运行机器本地，保存 manifest、哈希与来源指纹；W&B 记录配置、指标及按规则发布的 checkpoint 和最终评价产物。
- 正式运行启用源码快照，在 Hydra 输出目录的 `metadata/source_snapshot/` 保存 `source.tar.gz`、`manifest.json` 和 `runtime.json`，用于关联实际运行字节与本地来源。详见 [运行源码快照](docs/run-source-snapshot.md)。

启用了 W&B logger 的实验，应从对应 run 的 config、notes、metrics 与 summary 核对结果。配置校验或启动成功不等于训练完成或最终评价有效。

## 本地到运行端的代码同步

本地 Git 工作区是代码的可信源。同步配置为 `mutagen.yml`，只管理 `src/`、`configs/`、根目录 `.sh` / `.ps1`、`pyproject.toml` 与 `uv.lock`；远端 `.git/`、数据、模型、环境和实验产物不属于同步范围。

首次创建或终止后重建 session 时，从本地仓库根目录依次执行：

```powershell
./mutagen_sync.ps1 start
./mutagen_sync.ps1 status
./mutagen_sync.ps1 resume
```

`start` 创建暂停的 session。检查 `status` 中三个端点、`One Way Replica` 方向与 ignore 边界后再 `resume`。交给远端实验前执行 `./mutagen_sync.ps1 flush`；只有命令成功、三个 session 均为 `Watching for changes` 且无 conflict，才视为同步完成。

## 验证与文档

从根目录运行单元测试：

```powershell
uv run pytest
```

配置变更需进行 Hydra compose；脚本变更需检查 Bash 语法及参数解析；OpenSpec 覆盖的变更完成后运行 `openspec validate <change> --strict`。单元测试不启动完整训练或推理实验。

- [文档索引](docs/README.md)：当前实现、验证与历史材料的统一入口。
- [SASRec 基线](docs/sasrec-baseline.md)：序列推荐对照及数据协议。
- [本轮归档记录](docs/repository-cleanup-20261023.md)：五个已完成变更、正式规范与验证边界。
- [IntRR 基线](docs/intrr.md)：实现协议与已完成九格结果。
- 当前研究状态与计划由相邻 research 仓库的 `research-state.yaml` 和 `ideas/current-plan.md` 管理；历史文档与归档不自动恢复已暂停路线或授权新实验。

Git 保存说明文档、规格和归档索引。原始实验输出、日志、退役源码 ZIP 与其他大体积证据保留本地，具体保存边界见 [文档索引](docs/README.md#文件保存范围)。
