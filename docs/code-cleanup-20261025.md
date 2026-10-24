# 过时分析链路清理（2026-10-25）

## 清理依据与范围

根据用户的代码库清理请求，核对当前 `../research/research-state.yaml` 和 `../research/ideas/current-plan.md`：正式比较保留 TIGER、LIGER、BARS、LETTER、SASRec、IntRR，当前 M2/M3 已接受、剩余实验预算为0。早期 Tail-SID 与 TIGER 前缀候选干预不属于当前阶段。

删除三条可执行链路，共40个旧文件：

- `tail_sid_diagnosis`：根脚本、experiment、组件配置及 `src/quantization/tail_sid_diagnosis/`。
- `tiger_prefix_trace`：追踪脚本、配置、PrefixTrace schema、读取器和专用 datamodule。
- `tiger_prefix_allocation_probe`：干预脚本、配置和 `prefix_allocation.py`。
- 删除只被这些链路使用的 `DiagnosisDataset`、`CatalogDiagnosisDataset`、`DiagnosisDataModule`、batch 容器、frequency grouping preprocessing 与 collate。
- 删除对应专用测试，并从公共脚本／配置测试矩阵移除旧入口。

TIGER 删除 teacher-forcing trace、beam observation 和 reserve allocation 分支，保留正式合法前缀索引、普通受约束 beam、模型参数与统一训练入口。公共 `AuxiliaryTensorWriter` 继续服务 LIGER，调用方显式传入 `validator`，不再默认导入旧 TIGER schema。

## 保留边界

- 六种正式推荐方法、量化器与语义向量链路、LETTER 前置流程、当前 BARS M3 机制与贡献入口。
- 正式 CoPMRec 历史变体及 checkpoint 严格身份检查：旧 learned-alpha/dense 证据仍保持原身份。
- `load_training_item_frequency_tensor` 仍被 `copmrec_diagnosis` 使用，保留实现和测试。
- 原始数据、checkpoint、logs、W&B Artifact、冻结科学 JSON、历史结果与文档均保留。

历史链路复现使用清理前的 Git 版本与原科学输入；本次不改写旧实验结果，不启动训练、Testing 或远端实验，不操作外部记录，不创建提交。

## 验证

- 删除前保存小型 TIGER 的参数、输入及普通生成输出；删除后31个参数 tensor 初始化逐位一致，旧状态 strict load 成功，生成 SID 和累计分数逐位一致。
- 全部28个保留 experiment 完成 Hydra compose；三条旧入口的拒绝装配由结构测试覆盖。
- 聚焦51项测试通过，覆盖正式 TIGER、LIGER path writer、公共 writer、Artifact 读取和结构约束。
- 修改的 Python 文件通过 Ruff；`git diff --check` 通过。
- `openspec validate retire-tail-prefix-diagnostics --strict` 通过。八份旧能力规格由 REMOVED delta 撤销，历史正式规格等待变更归档时合并。
- 全库回归：`uv run --no-sync pytest -q`，1560 passed、1 skipped、4项第三方弃用警告（139.81秒）。之后新增的4项结构回归由包含7项检查的结构测试文件单独通过。
- 全部32个保留根脚本通过 `bash -n`；公共参数测试继续覆盖 quoting、空值、错误输入和额外 override。
