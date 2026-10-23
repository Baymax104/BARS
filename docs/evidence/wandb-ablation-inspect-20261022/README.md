# Ablation 非 Beauty seed42 runs 只读探查

项目：baymaxam/GRID。实际分组：['ablation_main']。共32个runs，保留16个Beauty seed42，候选删除16个。

判定使用实时完整config.dataset_name与config.seed，并与显示名逐项交叉核对。未修改任何W&B对象。

## 候选清单

| 数据集 | Seed | 训练Run | 测试Run |
| --- | ---: | --- | --- |
| beauty | 200 | `2cxk6qj9` | `6kv2woio` |
| beauty | 2026 | `afbmzinx` | `1zu4ucod` |
| sports | 42 | `hq166ou9` | `duw1ygvd` |
| sports | 200 | `8a7r4ys6` | `uxdgth7i` |
| sports | 2026 | `7doxj00o` | `no2rmohi` |
| toys | 42 | `jn3iqsep` | `d9v4prxh` |
| toys | 200 | `bhj57tye` | `yx09jggi` |
| toys | 2026 | `hnkajj6r` | `79ydiapf` |

## 范围及引用

- 16个候选均为Shared完整方法的训练/测试，属于Shared九格对照矩阵中的其他八格，并不是16种消融变体。
- 删除这些runs会使W&B Shared九格对照矩阵仅保留Beauty seed42的训练/测试。已有本地历史记录不等同于完整history或checkpoint备份。
- 候选关联用户可见artifact版本32个，逻辑大小1.528 GiB；系统artifact版本8个。
- 清单外W&B登记消费者关联条目：0。
- 本次仅探查runs；关联artifacts仅列出供审核，不自动纳入删除。若后续只删除runs，应使用delete_artifacts=False。

## 保留Run清单

- `rmgfscr0`：bars_v2_beauty_seed42_shared_train/2026-10-09_03-37-20
- `qhzzhnxp`：bars_v2_beauty_seed42_shared_no_mixture_train/2026-10-09_12-23-46
- `izwmwyig`：bars_v2_beauty_seed42_shared_no_joint_ce_train/2026-10-09_12-23-46
- `gtwv2c4n`：bars_v2_beauty_seed42_shared_no_residual_train/2026-10-09_12-23-46
- `lwtzxzre`：bars_v2_beauty_seed42_shared_fixed_alpha_one_train/2026-10-18_02-32-16
- `92gwx86m`：bars_v2_beauty_seed42_shared_fixed_alpha_one_test/2026-10-18_14-11-14
- `64mjlgze`：bars_v2_beauty_seed42_shared_test/2026-10-18_14-11-14
- `3yubqzcr`：bars_v2_beauty_seed42_shared_no_mixture_test/2026-10-18_14-30-21
- `fx6s5o4u`：bars_v2_beauty_seed42_shared_no_joint_ce_test/2026-10-18_14-31-05
- `xzfp1pgt`：bars_v2_beauty_seed42_shared_no_residual_test/2026-10-18_14-32-47
- `860tn67l`：bars_v2_beauty_seed42_untied_alpha_exploration_fixed_1_train/2026-10-20_20-45-18
- `fs5fgu76`：bars_v2_beauty_seed42_untied_alpha_exploration_fixed_1_test/2026-10-20_22-43-39
- `shwmvcol`：bars_v2_beauty_seed42_untied_alpha_exploration_fixed_0.5_train/2026-10-21_15-08-01
- `oqw8o4t7`：bars_v2_beauty_seed42_untied_alpha_exploration_init_0.0001_learned_train/2026-10-21_16-21-02
- `ybhdif6a`：bars_v2_beauty_seed42_untied_alpha_exploration_fixed_0.5_test/2026-10-21_17-13-22
- `na7kdgh2`：bars_v2_beauty_seed42_untied_alpha_exploration_init_0.0001_learned_test/2026-10-21_18-32-01

## 当前研究计划核对

已核对 ../research/ideas/current-plan.md 当前主版本段落：Shared仅保留Beauty42对照在M3；本次候选范围与该计划一致。旧Shared九格的历史数值及结论仍保持原版本事实。


## 后续执行结果

用户确认后已删除候选16个runs，均使用`delete_artifacts=False`；没有删除artifact。全项目runs从189降至173，ablation_main从32降至16，剩余全部为Beauty seed42。32个关联用户可见artifact的ID、digest、aliases和metadata前后相同，其余runs元信息及已完成指标未改变。详见`deletion-verification.json`及`execution-events.jsonl`。

## 关联Artifacts后续清理

用户另行要求删除artifacts后，已删除上述16个旧runs关联的32个用户可见artifact版本（16 code、8 checkpoint、8 recommendation_output），逻辑大小1,640,506,768字节，约1.528 GiB。删除前逐一核验ID/digest/aliases/metadata及无live消费者、无Registry链接。独立全量回读显示用户可见版本从363降至331，清单外artifact元数据未变，runs数量保持173。另有8份系统wandb-history由W&B后端管理并保留，未尝试绕过服务端限制。详见artifact-deletion-verification.json及artifact-deletion-events.jsonl。
