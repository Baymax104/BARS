# 已完成变更归档与提交（2026-10-25）

## 归档范围

按用户要求归档两项任务全部完成的变更，连同已验证的实现与当前文档形成一个完整 Git 提交：

- [retire-tail-prefix-diagnostics](../openspec/changes/archive/2026-10-25-retire-tail-prefix-diagnostics/proposal.md)：删除 Tail-SID、TIGER 前缀追踪与候选槽位干预，保持正式 TIGER 生成兼容。
- [rename-copmrec-to-bars](../openspec/changes/archive/2026-10-25-rename-copmrec-to-bars/proposal.md)：统一模块、类、配置、脚本与测试命名，保留已落盘协议与 checkpoint 身份。

两项均使用 `openspec archive <change> --yes` 合并正式规格，未跳过规格或验证。归档目录按用户 Asia/Shanghai 日期2026-10-25保存。

## 正式规格

- 撤销八份旧能力规格中的54项旧要求，分别保留一项明确退役要求，避免空规格及旧能力被继续当作活动要求。
- 新增 `retired-tail-prefix-surface` 与 `bars-engineering-naming`，共4项要求；连同上述退役要求，共新增12项要求。
- 活动变更列表为空。现有历史归档保持不变，两项本轮归档保存各自完整 proposal、design、tasks 和 delta。

## 验证与边界

实现最终全库回归为1571 passed、1 skipped；14种 BARS 变体的迁移前后 checkpoint／loss／dense及hybrid输出逐位一致，TIGER31个参数tensor与普通beam输出亦保持一致。28个experiment、89个项目Hydra target与32个根脚本已验证，完整证据见[清理记录](code-cleanup-20261025.md)和[命名迁移](bars-engineering-rename-20261025.md)。

本轮归档仅调整规格、归档目录和文档；提交前123项正式规格全部通过strict校验，26项聚焦结构回归全部通过，差异空白检查通过。没有新增训练、Testing、seed、预算、远端同步或外部记录修改。数据、checkpoint、日志与冻结科学证据不纳入清理删除。
