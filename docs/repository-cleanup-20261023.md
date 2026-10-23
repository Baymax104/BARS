# 已完成变更归档与项目文档同步（2026-10-23）

## 归档范围

按用户要求归档五个任务清单全部完成的 OpenSpec 变更。使用 `openspec archive <change> --yes` 合并正式规范并保存原始 proposal、design、tasks 和 delta，未使用跳过规范或跳过验证选项。

| 变更 | 完成内容 |
| --- | --- |
| `unify-experiment-display-naming` | 按研究角色统一 group，完整显示名，tokenizer 参数与显示组分离 |
| `promote-bars-fixed-half-no-mixture` | 当前固定 alpha=0.5、两损失 Untied 主方法及历史角色隔离 |
| `unify-bars-hybrid-evaluation` | 公共 hybrid 推理入口与 test／validation 显示阶段 |
| `use-hybrid-validation-for-bars-main` | hybrid Validation、严格选点来源及历史 dense 契约兼容 |
| `redo-bars-current-method-m3` | 当前三个匹配消融、固定模型机制与冻结预测贡献分析 |

原文件保存于 `openspec/changes/archive/2026-10-23-<change-id>/`。新增5项正式 capability，修改 `bars-untied-mechanism-study`；补齐 Purpose，解决早期命名规则与当前测试显示的冲突，并明确角色迁移、1/9回退和0/9重启均是历史时点。活动方法规格同步加入 IntRR，移除已经失效的“三种消融限定”。当前无活动变更。

## 文档与实现提交范围

- `AGENTS.md` 和 `README.md` 同步当前主方法、hybrid 选点、匹配 M3、显示分组、IntRR 和结果入口。
- `docs/copmrec-versions.md` 与文档索引同步当前命令、来源和历史边界。
- 纳入已有 BARS 变体、选点、机制／贡献分析、显示命名及对应测试改动；补齐运行面测试中遗漏的 IntRR 方法清单。
- 纳入当前 M2／M3 与 IntRR 已完成结果说明及证据 README。原始 JSON、CSV、日志和运行产物继续遵守 `.gitignore`，留在本地或运行端，不强制加入 Git。
- 只提交 GRID 仓库；相邻 research 仓库的状态、稿件和 PDF 改动由其自身版本管理。

## 验证

归档前五个变更均通过 `openspec validate <change> --strict`。归档后121项正式规范通过 strict 校验；10个改动 Bash 脚本通过 `bash -n`，改动及新增 Python 文件通过 `uv run ruff check`。

首次全量测试为1715 passed、1 skipped、1 failed；唯一失败是旧运行面断言遗漏已接入的 IntRR，已补齐。最终 `uv run pytest -q` 全量复验为 **1716 passed、1 skipped**，4项既有依赖弃用警告；配置 compose、脚本 quoting／空值／错误输入／override 透传验证均随现有测试通过。暂存区 `git diff --cached --check` 通过。

## 实验完成边界

本轮只引用已有独立验收记录：当前 BARS hybrid 选点主矩阵9/9；当前 M3 为 Beauty／seed42，三匹配消融、固定 Full 机制及配对贡献分析完成；IntRR 九格基线完成。旧 learned-alpha、三损失与 dense 选点结果保留独立历史身份。

本轮没有新增训练、Testing、模型 forward、seed、预算或外部记录清理。历史提案中的 W&B 删除及 Linear 更新只归档已有事实，不在本次重复执行。代码同步使用既有 Mutagen 三 session 和项目脚本；Git 不 push，不操作远端 `.git/`，Markdown 说明和规格由本地 Git 保存，不属于运行代码同步范围。
