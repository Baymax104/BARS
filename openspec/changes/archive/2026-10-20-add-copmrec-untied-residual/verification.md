# Shared / Untied 残差对照实现验收

验收更新：2026-10-19；变更创建于2026-10-18，协议标识保留创建日期。变更 `add-copmrec-untied-residual`，训练臂 `untied_residual`。初次实现交付完成本地验证，当时正式训练、Testing和远端同步核验均未执行；后续用户授权的实际启动见末节。

## 前置归档与提交

本次先归档已完成的三个提案，并合并主规格：`add-offline-dataset-adapters`、`add-copmrec-fixed-alpha-one`、`switch-copmrec-hybrid-deployment`。提交为 `8786b3b`（离线数据适配）和 `9b7c396`（fixed-alpha与hybrid部署）；归档前229项聚焦测试和归档后108份主规格strict通过。原LETTER结果文档改动保留在工作区。

## 模型行为与回归

从GRID仓库根目录执行：

```powershell
uv run --no-sync pytest tests/recommendation/test_copmrec_untied_residual.py -q
```

结果：49 passed。使用真实CPU小T5与内存目录，覆盖公共参数初值、构造/forward的dropout RNG、初始各loss一致、每项loss下shared梯度等于双侧梯度和、两侧直接影响路径、两表残差LR组、cold输出/梯度/权重、独立AdamW moments、fresh初始化与完整恢复后下一更新精确一致。破坏任一表、moments、参数组或身份被拒绝；旧五种shared来源仍严格兼容并与Untied双向隔离。不运行真实Trainer或完整experiment。

```powershell
uv run --no-sync pytest tests/recommendation/test_liger.py tests/recommendation/test_liger_probability_mixture.py tests/recommendation/test_copmrec_v2.py tests/recommendation/test_copmrec_hybrid.py tests/recommendation/test_copmrec_fixed_alpha.py tests/test_copmrec_entrypoint_retirement.py tests/data/components/test_m3_prediction_deployment.py -q
```

结果：132 passed，4条既有依赖deprecation warnings。覆盖LIGER默认行为、旧变体/严格恢复、概率mixture、dense Validation和hybrid候选/排序、原四bundle输入身份与退休入口。

## 配置与脚本

```powershell
uv run --no-sync pytest tests/test_copmrec_v2_config_script.py -q
```

结果：75 passed。实际Bash脚本通过uv stub解析，Hydra compose后检查双卡训练/单卡推理、两种notes、空值/错误输入、显式dry-run、额外override优先级、hybrid/dense身份、sharing/物理表数/比较协议和writer元数据；所有CoPMRec根脚本通过Bash语法检查。配置不新增experiment入口，diagnosis仍只接受原分析组合。

```powershell
uv run --no-sync ruff check src/recommendation/liger/module.py src/recommendation/copmrec/ablation.py src/recommendation/copmrec/residual.py src/recommendation/copmrec/protocol.py tests/recommendation/test_copmrec_untied_residual.py tests/test_copmrec_v2_config_script.py
uv run --no-sync ruff format --check src/recommendation/liger/module.py src/recommendation/copmrec/ablation.py src/recommendation/copmrec/residual.py src/recommendation/copmrec/protocol.py tests/recommendation/test_copmrec_untied_residual.py tests/test_copmrec_v2_config_script.py
openspec validate add-copmrec-untied-residual --strict
git diff --check
```

Ruff check、6文件format check、OpenSpec strict和diff检查通过。模型、配置和专项测试由独立agent复核，未发现阻断问题。

## 实验状态

唯一新增计划为Beauty seed42一次50k scratch训练及一次自身own-best的单卡hybrid Testing，Shared Full复用训练 `rmgfscr0` 和hybrid Testing `64mjlgze`。初次实现交付时未消费新增训练/Testing预算；已有650k训练成本及hybrid13+1闭环保留。新增残差参数为128N，实际全模型参数量和运行资源随真实执行登记。

完整中文协议、来源和手动命令见[研究计划](../../../../research/docs/copmrec-v2-untied-residual-plan-20261018.md)。初次交付时新实验ID、own-best、产物、指标及统计结果均保持null；实现验证不能替代正式DDP2/数据/产物审计。

研究侧验收通过：YAML全文件无重复键，旧研究状态块的原始字节保持，仅更新顶层日期并追加本补充块；current-plan仅更新日期及新增提示。新增计划/提示的局部链接均存在，新增执行和指标字段为空。两段完整手动Bash模板分别通过语法检查，经实际wrapper的uv stub输出再Hydra compose，训练DDP2/global256/50k和单进程hybrid beam20 Testing均匹配协议；未执行真实模型入口。差值约定统一为Shared减Untied，不按后续结果变更统计方向。

## 后续用户授权的同步与启动

2026-10-19用户进一步授权在Linear M3登记、同步node1并用tmux启动实验。BMX-184已创建并读回，状态In Progress；Mutagen flush及三个session核验通过。一次Untied训练已提交，W&B为g953gzcq，有限启动观察为running；双rank、配置、真实输入/source origin及已存step1000 checkpoint的双表/cold/optimizer状态均核验通过。训练未完成，最终own-best及Testing指标仍为空；准备阶段和旧实验成本保持原事实。详细启动来源见[执行回执](../../../docs/evidence/copmrec-untied-residual-launch-20261019/README.md)。


## 2026-10-19实验及配对统计结案

训练g953gzcq的50k/100次Validation/自身首次own-best step39500、hybrid Testing e4a3b038和22363用户配对统计均完成。独立指标复算最大误差3.47e-17，PCG64 seed42/2000次用户bootstrap及逐次重放一致；四项Shared−Untied区间均低于0，按协议登记untied_better。当前主方法不自动变更，不追加实验。BMX-184 Done；完整数值、来源与参数成本见[正式结果](../../../../research/docs/copmrec-v2-untied-residual-results-20261019.md)。
