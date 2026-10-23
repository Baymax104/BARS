# W&B 过时 runs 与 artifacts 清理清单

状态：用户已确认，16个runs和50个用户可见artifact版本已删除并独立核验。项目：`baymaxam/GRID`。盘点时共205个runs（204 finished，1 running）。

执行结果：删除16个history组runs、50个用户可见artifact版本；11个wandb-history系统artifact仍由后端保留，未随run清除。用户可见artifact逻辑大小合计1.705 GiB，实际释放空间受W&B去重与回收策略影响。

## 判定依据

- 当前主方法为固定alpha=0.5且不含mixture loss；旧Untied三损失矩阵归history。
- 保留旧Beauty42来源g953gzcq/e4a3b038及全部所属产物：仍被mechanism_main分析使用。
- 删除其余八格的8训练与8测试；已逐项检查其发布产物，没有保留组的W&B登记消费者。
- 清理17份来源run已不存在且无W&B登记消费者的源码版本，以及明确退役dense测试tf18g4ec遗留的预测版本。
- 保留bars_main、ablation_main、mechanism_main、所有baseline和上游组；不根据temporary标签或时间直接删除。
- historical snapshots保留config、summary和notes；未备份完整history、checkpoint或artifact文件，存储清理不修改历史实验事实。

## Run 精确清单

| Run ID | 名称 |
| --- | --- |
| `4r4zx78u` | bars_v2_beauty_seed200_untied_train/2026-10-19_04-14-42 |
| `oblbespc` | bars_v2_beauty_seed2026_untied_train/2026-10-19_05-55-58 |
| `ow9keoti` | bars_v2_sports_seed42_untied_train/2026-10-19_07-26-51 |
| `s5a3wvfq` | bars_v2_sports_seed200_untied_train/2026-10-19_09-16-19 |
| `9vnepv70` | bars_v2_beauty_seed200_untied_test/2026-10-19_13-40-47 |
| `wgen76v1` | bars_v2_beauty_seed2026_untied_test/2026-10-19_13-40-47 |
| `02jd25ht` | bars_v2_sports_seed200_untied_test/2026-10-19_13-42-44 |
| `x36rvxfr` | bars_v2_sports_seed42_untied_test/2026-10-19_13-42-44 |
| `86odzgh1` | bars_v2_sports_seed2026_untied_train/2026-10-19_13-45-19 |
| `39313apw` | bars_v2_toys_seed42_untied_train/2026-10-19_15-48-33 |
| `ljlwvdh2` | bars_v2_toys_seed200_untied_train/2026-10-19_18-24-42 |
| `zurt85mz` | bars_v2_toys_seed2026_untied_train/2026-10-19_21-13-54 |
| `u0p3a36m` | bars_v2_sports_seed2026_untied_test/2026-10-19_21-27-35 |
| `kdrqzc7i` | bars_v2_toys_seed42_untied_test/2026-10-19_21-30-14 |
| `ibwgb7z2` | bars_v2_toys_seed200_untied_test/2026-10-19_21-32-05 |
| `kq3j4vm5` | bars_v2_toys_seed2026_untied_test/2026-10-19_23-53-42 |

## Artifact 精确清单

| Artifact版本 | 类型 | 字节 |
| --- | --- | ---: |
| `grid-source-4r4zx78u:v0` | code | 349956 |
| `copmrec_v2_beauty_seed200_untied_residual_train-checkpoint:v0` | checkpoint | 201438101 |
| `grid-source-oblbespc:v0` | code | 349956 |
| `copmrec_v2_beauty_seed2026_untied_residual_train-checkpoint:v0` | checkpoint | 201438101 |
| `grid-source-ow9keoti:v0` | code | 349956 |
| `copmrec_v2_sports_seed42_untied_residual_train-checkpoint:v0` | checkpoint | 246637653 |
| `grid-source-s5a3wvfq:v0` | code | 349956 |
| `copmrec_v2_sports_seed200_untied_residual_train-checkpoint:v0` | checkpoint | 246637653 |
| `grid-source-9vnepv70:v0` | code | 349956 |
| `copmrec_v2_beauty_seed200_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 7337141 |
| `grid-source-wgen76v1:v0` | code | 349956 |
| `copmrec_v2_beauty_seed2026_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 7337141 |
| `grid-source-02jd25ht:v0` | code | 349956 |
| `copmrec_v2_sports_seed200_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 11678261 |
| `grid-source-x36rvxfr:v0` | code | 349956 |
| `copmrec_v2_sports_seed42_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 11678261 |
| `grid-source-86odzgh1:v0` | code | 349956 |
| `copmrec_v2_sports_seed2026_untied_residual_train-checkpoint:v0` | checkpoint | 246637717 |
| `grid-source-39313apw:v0` | code | 349956 |
| `copmrec_v2_toys_seed42_untied_residual_train-checkpoint:v0` | checkpoint | 200159253 |
| `grid-source-ljlwvdh2:v0` | code | 349956 |
| `copmrec_v2_toys_seed200_untied_residual_train-checkpoint:v0` | checkpoint | 200159253 |
| `grid-source-zurt85mz:v0` | code | 349956 |
| `copmrec_v2_toys_seed2026_untied_residual_train-checkpoint:v0` | checkpoint | 200159253 |
| `grid-source-u0p3a36m:v0` | code | 349956 |
| `copmrec_v2_sports_seed2026_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 11678261 |
| `grid-source-kdrqzc7i:v0` | code | 349956 |
| `copmrec_v2_toys_seed42_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 6369205 |
| `grid-source-ibwgb7z2:v0` | code | 349956 |
| `copmrec_v2_toys_seed200_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 6369205 |
| `grid-source-kq3j4vm5:v0` | code | 349956 |
| `copmrec_v2_toys_seed2026_untied_residual_hybrid_inference-recommendation-output:v0` | recommendation_output | 6369205 |
| `bars_temp_beauty_seed42_untied_alpha05_no_mixture_dense_test_20261021-221409-recommendation-output:v0` | recommendation_output | 7337141 |
| `grid-source-tf18g4ec:v0` | code | 351952 |
| `grid-source-zaonc18v:v0` | code | 351104 |
| `grid-source-exxld81t:v0` | code | 351104 |
| `grid-source-e4bk7zkb:v0` | code | 350620 |
| `grid-source-2n4nydm6:v0` | code | 327058 |
| `grid-source-842spx3x:v0` | code | 314181 |
| `grid-source-ooq7yb16:v0` | code | 314181 |
| `grid-source-bo7onju4:v0` | code | 314181 |
| `grid-source-np5t08pl:v0` | code | 314181 |
| `grid-source-ycaka1w6:v0` | code | 314181 |
| `grid-source-utlknq9f:v0` | code | 314181 |
| `grid-source-jdlzbwsh:v0` | code | 314181 |
| `grid-source-gvm6gwfn:v0` | code | 314181 |
| `grid-source-lcv4q1iu:v0` | code | 314181 |
| `grid-source-ryeasjzr:v0` | code | 314181 |
| `grid-source-3oi4z5kj:v0` | code | 314181 |
| `grid-source-57jvuy59:v0` | code | 314181 |

## 执行约束

用户确认后先重新核对状态、精确ID、alias和消费者，再删除清单内版本与runs。运行中run和清单外对象不变更。任何新增保留消费者或状态变化均跳过该对象并记录。系统history优先通过run删除处理；回读发现仍保留后，尝试清理首个明确列出的系统版本，W&B后端拒绝并返回cannot delete system managed artifact，未继续尝试其余系统版本。

plan.json SHA256：`453bb96712c2b7020ff8b3c3d0e287b0c899717b25b821e96c8a6db737299e9f`。

## 执行验收

- 北京时间2026-10-22执行，用户已明确确认删除。
- Runs从205降至189，精确减少清单内16个；保留runs的名称、group、tags、config、notes及finished runs的summary未改变。
- 用户可见artifact版本从413降至363，精确减少清单内50个；保留版本的ID、版本号、状态、size及aliases未改变。
- 删除逻辑大小1,830,522,111字节，约1.705 GiB；不等于已实际回收的存储字节。
- 11个系统history版本仍可读取，W&B API禁止独立删除，返回`cannot delete system managed artifact`。属于服务端管理的残留，未强行绕过。
- `execution-preflight.json`保存删除前复核；`execution-events.jsonl`逐项记录；`verification.json`和删除后inventories保存独立回读结果。
