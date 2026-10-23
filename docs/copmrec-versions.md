# BARS（CoPMRec v2）当前方法与运行入口

更新：2026-10-23。当前主方法为 `untied_fixed_alpha_half_no_mixture`，采用固定 alpha=0.5、SID CE／Catalog CE／mixture NLL 权重1/1/0。实现继续使用 `copmrec` 入口；显示名与研究角色不改变内部 checkpoint、Artifact 或协议身份。研究状态及预算以相邻 research 仓库的状态和计划为准。

## 当前配方与评估

历史侧和目录侧分别使用独立、零初始化的128维商品残差表，内容投影共享，两表 residual LR 为0.002，cold 残差恒零。目录 posterior 聚合合法前缀 mass，与 decoder 概率以固定0.5混合生成 beam20；候选与全部 cold 商品合并、去重后，以 joint catalog logits 和 stable catalog-row ties 输出 Top10，不排除历史商品。仍计算全目录 logits／prefix mass，已有质量结果不代表效率优势。

当前主方法和匹配消融均为 scratch 50k、双进程 FP32，每500步 hybrid Validation，按自身首次最高 `val/ndcg@10` 选点。正式推理单进程，核验自身 own-best checkpoint 的 URI、SHA256、变体及选择协议。公共推理脚本默认 hybrid，拒绝 dense 部署及不符合协议的 override；历史变体保留其原 dense 选点契约，不允许跨协议恢复。训练后不自动 Testing。

| 角色 | variant | SID／Catalog／mixture | 默认 group |
| --- | --- | --- | --- |
| 当前 Full，Untied | `untied_fixed_alpha_half_no_mixture` | 1/1/0 | `bars_main` |
| 当前 Shared | `shared_fixed_alpha_half_no_mixture` | 1/1/0 | `ablation_main` |
| 当前双侧零残差 | `no_residual_fixed_alpha_half_no_mixture` | 1/1/0 | `ablation_main` |
| 当前 Untied 去 Catalog CE | `untied_fixed_alpha_half_no_joint_ce_no_mixture` | 1/0/0 | `ablation_main` |

三个当前消融使用协议 `bars-fixed-half-hybrid-m3-20261023-v1`。Shared 同时改变容量、共享约束与梯度耦合；去 CE 移除当前唯一目录判别目标，不能套用历史三损失解释。裸 `copmrec_train.sh` 运行历史 learned-alpha Shared，不是上表的匹配 Shared。

## 根目录命令

以下变量需替换为冻结数据、对齐的 SID／content bundle，以及本单元自身 own-best checkpoint 和64位小写 SHA256。训练和 Testing 分别授权，不因示例而启动新实验。

```bash
CUDA_VISIBLE_DEVICES=0,1 NPROC_PER_NODE=2 bash ./copmrec_ablation_train.sh \
  --variant untied_fixed_alpha_half_no_mixture --dataset beauty --seed 42 \
  --devices '[0,1]' --data-dir "$DATA_DIR" \
  --semantic-id-path "$SEMANTIC_ID_PATH" --embedding-path "$EMBEDDING_PATH" \
  --notes "BARS Untied；fixed alpha=0.5；no mixture NLL；50k scratch"

CUDA_VISIBLE_DEVICES=0 NPROC_PER_NODE=1 bash ./copmrec_ablation_inference.sh \
  --variant untied_fixed_alpha_half_no_mixture --dataset beauty --seed 42 \
  --devices '[0]' --data-dir "$DATA_DIR" \
  --semantic-id-path "$SEMANTIC_ID_PATH" --embedding-path "$EMBEDDING_PATH" \
  --checkpoint "$OWN_BEST_URI" --checkpoint-sha256 "$CHECKPOINT_SHA256" \
  --split testing --notes "BARS Untied；自身own-best；Testing"
```

当前消融替换为表中的 variant，并使用各自 checkpoint。脚本支持 `--dry-run`、两种 notes 写法和尾随 Hydra override。检查组合配置可使用 `uv run -m src.main experiment=copmrec_ablation_train ablation_variant=untied_fixed_alpha_half_no_mixture --cfg job`，无需启动训练。

显示分组默认按研究角色统一，显示名区分方法、数据集、seed、变体及阶段，BARS 阶段为 `train`／`test`／`validation`。旧 `untied_residual` 显示归入 `history`；具体映射见 `configs/logger/bars_display.yaml`。

## 当前证据与机制入口

据本地保存的独立验收回执，[M2 九格](bars-hybrid-m2-results-20261023.md)全部完成当前 hybrid 选点训练与各一次自身 own-best Testing；[当前 M3](bars-current-method-m3-results-20261023.md)完成 Beauty／seed42 三个匹配消融、固定 Full 生成／排序干预和零 forward 配对贡献分析。M3 仅支持该训练来源，不扩为跨 seed 机制结论，追加实验及预算为0。

`bars_untied_mechanism.sh --analysis generation` 默认当前 Full，比较 production 固定0.5／alpha0 生成与 catalog／合法 decoder 完整 SID logP 排序；production＋catalog 必须逐用户精确复现冻结正式 Top10。`--analysis contributions` 通过 CPU `Trainer.test` 读取显式预测 URI／SHA 和匹配变体，拒绝缺失比较来源，不新增模型 forward。历史来源须显式指定 `analysis_source_variant=untied_residual` 并提供原始来源；不能将旧结果填为当前方法机制证据。

## 历史边界

旧 `untied_residual`、`untied_no_joint_ce`、Shared 根入口及其他 alpha 探索继续保留原模型、损失和恢复身份。[2026-10-19 M3](bars-untied-mechanism-results-20261019.md)及[旧 Untied M2](evidence/bars-untied-m2-final-20261019/README.md)使用其实际 learned-alpha／三损失／dense 选点来源，不计入当前矩阵。历史 `--deployment dense` 命令不再是公共脚本的有效入口。

`copmrec_diagnosis.sh` 的 hits／residual／prefix 保留原 Shared 分析身份；旧四来源不由当前 Full 隐式替换。旧版本定义与退役实现仅供文档追溯，见[历史版本总结](archive/copmrec-development-20261006/versions.md)及[运行源码归档](archive/copmrec-v0-v1-runtime-20261009/README.md)。本轮实现归档见[整理记录](repository-cleanup-20261023.md)。
