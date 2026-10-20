# IntRR 验证编码复用与队列交接

## 变更与等价范围

模型模块提案 `optimize-intrr-validation-encoding` 已实现：eval_step 只调用一次 encode_history，随后将同一 user_state 和 alignment_loss 传给私有 loss 和 beam 方法。公共 losses、generate、训练计算、模型参数及 intrr_contract 保持兼容。未引入跨 batch 缓存。

回归测试用相同权重的独立副本执行旧公共 losses + generate 组合，覆盖 validation_step、test_step、dropout=0.15 的 eval 模式、重复 UID、不同长度历史、16 叶节点的 Top10 和 5 叶节点窄树。所有 loss、SID、分数及标签逐元素完全相同（rtol=atol=0）；backbone 调用由两次变成一次。旧实现四例均在次数断言失败。共享 RAN 梯度、独立完整路径枚举和 strict checkpoint 加载测试同时通过。

验证结果：模型/RAN/backbone 74 passed，配置/数据 67 passed，共 141 项。两个模块均通过 OpenSpec strict 验证。模型检查为内存 CPU 测试；没有额外启动 dry-run、5step 或正式实验，未产生需要清理的临时运行记录。实际 GPU 验证提速幅度待后继运行测量，不能由编码次数直接换算；其他用户 GPU 争用仍可能主导耗时。

## 独立交接模块

`track-intrr-validation-rollout` 在 train experiment 添加 `validation_implementation: history-encoding-reuse-v1`。它只标记实现，不改变模型构造和 TIGER 协议。运行源码差异仅为该配置与 IntRR module 两份文件；新 source SHA256 为 `2447de596b5742ac3445fdac04f171b2b20bed0401098bb4c3eb12c5e3d98b07`，旧版本为 `390eee7aaadcebe354b1c29a7d50f7dd27778cd1218bb28b4077a84c5228f8d4`。

当前 Beauty/seed200（BMX-197，swu5s4wy）继续原版本自然结束。修改本地源码前已暂停 Mutagen 三 session，远端原来源 verified。原队列 guard 的副本及原 preflight 保留；新 guard 在 preparing 阶段返回等待码 3，实测通过。七个既有 tmux wrapper、run ID 和训练预算保持。

一次性交接脚本 [complete-handover.ps1](evidence/intrr-validation-optimization-20261020/complete-handover.ps1) 等待首格 exit0、50k 后核对本地固定哈希，依次执行 Mutagen resume、flush、status，确认三 session Watching 且无 conflict，再核验远端来源。成功后保留旧身份、更新七格 unit.json 的新实现身份，原子发布 ready 清单。任一核验失败均保持队列等待。资源 guard 继续检查 GPU0/7 的其他用户进程、可用显存、端口、磁盘与固定数据哈希。

## 交接结果

用户随后明确允许其他GPU的多余显存，后续七格已在02:05左右切换至GPU4/5；Beauty2026已启动，其余六格等待前驱。该调整保留验证优化版本及所有训练协议，详情见[GPU资源切换记录](evidence/intrr-gpu-switch-20261020/README.md)。下方GPU0等待记录为切换前状态。

2026-10-20 北京时间01:44左右，原 Beauty200 正常结束，未重启。零forward完成审计核准 W&B finished、50k、完整500次验证和首次最高val/NDCG@10的 step49,900（0.04216626286506653），保留 checkpoint SHA256 `b4fb975ac0e250b0fc989b34bdeceac02fab50a70efa9a50f5184352cd2862be`；尚未Testing，不作为本格最终推荐指标。

01:44:50新版本完成交接：Mutagen resume、flush成功，三个session均Watching且无冲突，远端来源verified。原首格快照仍为旧哈希；原preflight保留，七个后继unit明确记录新旧哈希及实现标记。

BMX-198 Beauty2026／预留W&B ID ppg0xyqx 的现有tmux已进入新版本资源guard，当前日志为 `waiting: GPU0 has another user's process`。它尚未创建训练run，满足原资源条件后自动起训；其余六格等待各自前驱。没有通过绕过guard再次进入跨用户GPU争用，也未新增训练格、重试或Testing。

完整执行状态见 [证据目录](evidence/intrr-validation-optimization-20261020/README.md) 和其 JSON。
