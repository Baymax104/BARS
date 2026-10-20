# GRID 文档索引

项目概览、环境安装与当前运行入口见[项目首页](../README.md)。

## 当前入口

- [BARS 方法与运行入口](copmrec-versions.md)：Untied主方法、Shared对照、三项训练目标、现有可执行入口及各自证据范围。
- [BARS Untied Beauty42机制结果](bars-untied-mechanism-results-20261019.md)：三组实验和独立验收完成，商品适配、直接目录CE及生成／排序互补作用支持当前论文主线；附真实来源与阶段决定。
- [BARS Untied Beauty42机制计划](bars-untied-mechanism-plan-20261019.md)：保留共同零残差贡献、双表去目录CE与固定checkpoint生成／排序2×2的原问题、判断规则及执行记录。
- [BARS Untied 论文主线](../../research/docs/bars-untied-narrative-20261019.md)：固定内容索引上的商品行为适配与生成排序，附[Beauty42直接配对统计](evidence/bars-untied-narrative-20261019/README.md)。
- [LETTER 实现](letter.md)与[验证记录](letter-validation.md)：CF teacher、Tokenizer、SID 导出及推荐链路。
- [SASRec 基线](sasrec-baseline.md)与[实现计划](sasrec-implementation-plan.md)：数据、算法骨干和训练推理协议。
- [IntRR 基线](intrr.md)：分模块接入、TIGER通用配置、[Beauty三seed结果](intrr-beauty-three-seed-results-20261020.md)与[M4完整矩阵计划](intrr-m4-plan-20261019.md)；完整矩阵当前3/9，其余单元继续训练。
- [2026-10-20归档与提交记录](repository-cleanup-20261020.md)：八个已完成实现提案、正式规范合并与实验完成边界。
- [运行源码快照](run-source-snapshot.md)：本地可信来源、运行端字节归档与 W&B code Artifact。
- [2026-10-09 整理记录](repository-cleanup-20261009.md)：OpenSpec 归档范围、规格合并边界和提交分组。

当前研究版本、实验状态和预算以 `../../research/research-state.yaml` 与 `../../research/ideas/current-plan.md` 为准。代码行为以当前 `src/`、`configs/` 和根目录脚本为准。

## 历史记录

带日期的实验文档、`archive/` 和 `evidence/` 中的说明保留记录时的事实，旧文档中的“当前版本”、命令和任务状态不代表今日运行面。尤其是早期 `copmrec-v2.md` 所指的开发版本，不等同于 2026-10-09 的正式 v2；请从上面的正式版本索引进入。

开发阶段的做法、指标与决策边界集中在[历史版本总结](archive/copmrec-development-20261006/versions.md)。历史文档副本、运行目录快照和迁移前计划保存于本地证据目录，避免在版本库中重复维护。

归档保存历史事实，不恢复已退役实现、旧研究结论或预算。功能变更归档也不表示对应正式训练和 Testing 已完成。

## 文件保存范围

Git 保存以下内容：

- `docs/` 根目录的直接说明文档。
- `archive/<归档名>/` 的直接说明、历史版本总结与索引。
- `evidence/<证据名>/README.md`，以及 `.gitignore` 明确保留、被正文引用的指标、诊断和命令说明。

原始 JSON、CSV、日志、图片、论文附件、退役源码 ZIP、运行目录副本、迁移前文档快照和临时 issue 内容均保留本地。Markdown 扩展名不自动意味着需要纳入 Git；历史索引中指向这些本地快照或原始输出的相对链接，需要相应本地证据才能打开。

退役入口单元测试直接核验旧文件退出、旧 experiment 无法 compose 及保留入口可用，不再读取文档目录中的 ZIP 或 manifest。ZIP 的 CRC、大小与 SHA256 属于本地归档核验，不是代码单元测试的前置条件。
