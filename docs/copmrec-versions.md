# CoPMRec 当前正式版本

当前主版本为 **CoPMRec v2 hybrid（可学习 alpha 的 Full）**。默认模型 `src.recommendation.copmrec.CoPMRec`，训练 `copmrec_train.sh`、推理 `copmrec_inference.sh`；所有阶段无历史排除，三项等权loss为SID CE、joint catalog CE、mixture NLL，无native view。默认推理使用 checkpoint 自身 learned-alpha mixture 生成20条 beam 候选，过滤非法SID，并入全部cold商品、去重后，在候选内按同一joint catalog logits稳定catalog-row排序，输出Top10；alpha参与候选概率，不是最终dense评分权重。

训练仍按原50k日程运行，每500步raw full-catalog dense Validation按 `val/ndcg@10` 选自身own-best。既有训练checkpoint、seed、变体、完整状态和SHA256继续严格核验；新 `copmrec-hybrid-deployment-v1` 仅登记本次部署，不修改旧训练身份。旧全目录dense结果保留为辅助证据，可用 `--deployment dense` 显式复现；默认 `inference_deployment_mode=hybrid`，命令行也支持 `--deployment hybrid`。

消融入口 `copmrec_ablation_train.sh` / `copmrec_ablation_inference.sh`，允许no_mixture、no_residual、no_joint_ce及固定端点fixed_alpha_one。hybrid下no_mixture删除mixture NLL并使用冻结alpha=0.5，作为系统消融报告；no_residual/no_joint_ce使用各自checkpoint的learned alpha，fixed_alpha_one使用精确1。机制入口 `copmrec_diagnosis.sh`：hits、residual、prefix；hits使用正式hybrid Full/no_mixture/no_residual/no_joint_ce四bundle，原四来源定义保持不变；residual保留dense评分分析身份，prefix保留训练真实前缀分析身份。Trainer.test单卡、不更新权重。group继续使用paper_main/ablation/mechanism_copmrec_<dataset>，推理task/tag/metadata明确v2与实际部署模式。

2026-10-18 增补 `--variant fixed_alpha_one`：三目标权重仍均为1，训练 mixture 精确使用目录 mass（alpha=1），冻结 gate 并从 optimizer 排除；与 Full 使用独立 checkpoint 身份。Beauty seed42 一臂50k训练已完成，W&B run为 `lwtzxzre`，dense Testing `2n4nydm6` 已完成并通过独立审计，使用47,500步own-best；Full复用BMX-120。协议、命令、预算及结果边界见[固定alpha=1比较计划](../../research/docs/copmrec-v2-fixed-alpha-one-plan-20261018.md)，训练启动事实见[启动回执](evidence/copmrec-fixed-alpha-one-launch-20261018/README.md)，完成结果见[dense Testing审计](evidence/copmrec-fixed-alpha-one-test-20261018/README.md)。

2026-10-18 用户已批准hybrid主部署迁移：新增范围为9次Full、3次Beauty42系统消融、1次alpha1正式推理和1次零forward hits，新增训练为零。逐格来源、执行进度及产物见[hybrid迁移计划](../../research/docs/copmrec-hybrid-migration-plan-20261018.md)；对应Linear为[主矩阵BMX-168](https://linear.app/baymax104/issue/BMX-168)、[系统消融BMX-169](https://linear.app/baymax104/issue/BMX-169)和[hits分析BMX-183](https://linear.app/baymax104/issue/BMX-183)。旧dense与临时hybrid结果保留各自身份，不替代新正式矩阵；当前实现仍计算全目录logits/prefix mass，此次迁移不包含效率改善主张。

从仓库根目录执行下例；变量分别填入冻结的数据目录、SID/content bundle与该单元自身own-best URI/SHA256，设备为当前单进程的逻辑编号。省略 `--deployment hybrid` 时仍默认hybrid；将其改为 `--deployment dense` 可进行辅助dense推理。变体使用 `copmrec_ablation_inference.sh --variant <variant>` 并传入相同来源参数。

```bash
bash ./copmrec_inference.sh --deployment hybrid --dataset beauty --seed 42 \
  --devices '[0]' --data-dir "$DATA_DIR" \
  --semantic-id-path "$SEMANTIC_ID_PATH" --embedding-path "$EMBEDDING_PATH" \
  --checkpoint "$OWN_BEST_URI" --checkpoint-sha256 "$CHECKPOINT_SHA256"
```

旧native/history控制、joint-only临时别名、v1评估、预算续训和混合终排入口已退出运行面；必要的共享组件收敛在copmrec包，LIGER原基线行为保留。历史源码和测试逐字备份见[运行源码归档](archive/copmrec-v0-v1-runtime-20261009/README.md)。旧v0/v1定义与指标只在文档保存，不提供旧版可执行入口。

[方法定义](../../research/docs/copmrec-v2-formal-definition-20261009.md)、[总计划](../../research/docs/copmrec-v2-experiment-plan-20261009.md)、[历史结果](../../research/docs/copmrec-v0-v1-results-archive-20261009.md)、[原运行面迁移核验](evidence/copmrec-v2-consolidation-20261009/README.md)。2026-10-09运行面收敛迁移本身未启动实验；用户后续授权的M2九次训练与九次单卡dense Testing均已完成并通过独立审计，见[dense完成结果](evidence/copmrec-v2-m2-test-20261009/README.md)；[启动回执](evidence/copmrec-v2-m2-launch-20261009/README.md)保留启动时的事实。

