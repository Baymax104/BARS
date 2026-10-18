# 固定 alpha=1 比较的准备核验

日期：2026-10-18。初次交付为实现与实验准备，该阶段训练、Testing、远端同步均未执行。用户随后明确授权 node1 tmux 执行且不持续监控；下文保留阶段记录，最终完成状态见末节。

## 本地验证

从 GRID 根目录执行：

```powershell
uv run --no-sync pytest tests/recommendation/test_copmrec_v2.py tests/recommendation/test_copmrec_fixed_alpha.py tests/recommendation/test_liger_probability_mixture.py tests/test_copmrec_v2_config_script.py tests/test_copmrec_entrypoint_retirement.py -q
openspec validate add-copmrec-fixed-alpha-one --strict
```

结果：124 passed；OpenSpec strict 通过。修改的7个 Python 文件通过 Ruff check 和 format check，目标 tracked 文件 diff check 通过。

验证范围：精确端点、mixture loss 与 catalog CE/H 及总梯度关系、公共初值与 dropout RNG、全部可训练参数有限梯度、冻结 gate 不进入 optimizer、自身 checkpoint 恢复和错误身份拒绝；旧三臂/Full/前缀诊断回归；Bash launcher 的 uv stub、Hydra compose、双卡训练/单卡推理参数、两种 notes、显式 dry-run、override 优先级及非法输入，根目录 CoPMRec 脚本语法。

研究文档另通过 YAML 无重复键和 OmegaConf 解析、Full 参考数值与当前状态精确一致、旧 M3 Done/150k 保留、新臂结果字段全 null、600k已花/650k计划一致性检查。两段文档 Bash 命令通过 Git Bash 语法检查；Testing 前置变量检查覆盖5例，不执行真实模型或服务。

独立只读复核未发现实质问题。内存梯度验证支持实现可用性，不代表已经完成实际 DDP2 训练验证。

## 准备阶段的计划与外部登记

研究协议为 `E:/projects/research/docs/copmrec-v2-fixed-alpha-one-plan-20261018.md`；研究状态键 `fixed_alpha_one_comparison_20261018`，状态 `prepared_not_started`。

[BMX-166](https://linear.app/baymax104/issue/BMX-166/copmrec-v2-增补-固定-alpha1-vs-可学习混合beauty-seed42) 已创建并回读：Todo、M3“机制消融”、标签“机制”，关联 BMX-120 / BMX-157 / BMX-163；十章完整，运行命令及结果登记代码块与最终本地计划逐字一致，核心条件已核对。平台自动将链接和 issue 引用规范化。BMX-157 与原已完成实验保持原完成身份。

新增计划仅 Beauty seed42：复用 learned Full，增加 fixed_alpha_one 的一次50k scratch训练和一次自身单卡Testing；各类结果的处理与归因边界已预登记。完整运行仍由用户手动启动。

## 后续授权启动

用户后续明确要求在 node1 通过 tmux 启动且不持续监控。已完成 Mutagen flush 及三 session 状态核验，在物理 GPU1、7 启动唯一新增训练，W&B run=`lwtzxzre`；有限启动核验记录到 global step549、alpha=1、有限loss和首次step500 Validation/checkpoint。当时Testing未执行、未排队，未等待50k完成或设置持续监控。实际命令、会话和记录见[启动回执](../../../../docs/evidence/copmrec-fixed-alpha-one-launch-20261018/README.md)。

## 归档前最终验收

训练 `lwtzxzre` 已完成50k更新和100次训练内Validation，按自身首次最高raw val/NDCG@10选择step47500。后续获用户授权的单卡dense Testing `2n4nydm6` 已finished/exit0，22363名用户、checkpoint SHA256、输入来源、合法唯一Top10及四指标和配对区间通过独立审计，研究状态为 `completed_audit_passed`，BMX-166已Done。详见[正式Testing回执](../../../../docs/evidence/copmrec-fixed-alpha-one-test-20261018/README.md)。

此后默认部署由独立hybrid迁移提案更新；fixed_alpha_one的hybrid Testing `92gwx86m` 已随13次正式推理及一次零forward分析完成并通过审计，原dense证据继续保留。详见[hybrid迁移回执](../../../../docs/evidence/copmrec-hybrid-migration-20261018/README.md)。本提案的一次50k训练及一次自身dense Testing预算已闭环，归档不追加训练、推理或扫描预算。
