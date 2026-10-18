# 离线数据适配器验证回执

验证日期：2026-10-17。变更：`add-offline-dataset-adapters`。

## 本地验证

- 定向 pytest：135 passed；4条第三方弃用提示，不影响通过。
- 覆盖：两个 Adapter、唯一邻居迭代 core、重复保留/显式去重、时间与源行排序、确定映射及压缩分片、共同切分、异常数据拒绝、临时目录边界、CLI/profile、原有 TIGER/LIGER/CoPMRec 共用输入、SASRec、LETTER/CF、量化 ItemBatch、worker 文件分配及脚本参数。
- Ruff check/format、`bash -n letter_common.sh` 和 `openspec validate add-offline-dataset-adapters --strict` 通过。
- `src/main.py`、launcher、模型、batch 定义、collate、reader 无修改。保留用户原有文档工作区变化。

## 同步

按仓库入口暂停已有 session，在本地通过后 resume、flush。三个端点均为既定 GRID 路径，One Way Replica、代码范围及排除边界已核对；三个 session 均为 `Watching for changes`，无冲突。数据、checkpoint、虚拟环境和 Git 未参与同步。运行时五个准备模块文件的 SHA256 与本地一致。

## node1 dry-run

远端回执目录：`/data3/weizhenyu/projects/GRID/data/preparation-receipts/offline-adapters-20261017-092556/`。

两来源均使用默认正式过滤与分片参数，仅增加 `--dry-run --max-records 500000 --report ...`，未自动降低 core、减少分片或执行完整 experiment。每份源文件最多读取500,000条记录。

| 数据集 | metadata实际读取 | 交互实际读取 | 样本过滤后用户 | 样本商品 | seen / cold | 退出码 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Steam | 32,135 | 500,000 | 5,398 | 568 | 564 / 4 | 0 |
| Home and Kitchen | 436,988 | 500,000 | 57,412 | 23,807 | 23,772 / 35 | 0 |

每来源32个商品分片、training/evaluation/testing各128分片，均为非空；416个分片全部回读内容与预期行一致，用户身份、留出前缀及目录范围校验通过。临时准备数据目录已释放；TMPDIR下仅留 uv 自身锁文件。正式 `prepared/full_5core_v1` 目录未创建，源数据未写入。

这证明有界前缀样本上的数据适配与回读契约，不是完整数据集统计，不建立模型性能、正式数据准备或实验完成结论。

- [汇总验证](validation.json)
- [Steam完整dry-run manifest](steam-dry-run.json)
- [Home and Kitchen完整dry-run manifest](home_and_kitchen-dry-run.json)
