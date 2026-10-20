# IntRR Beauty 三 seed Testing 与训练队列恢复

用户在2026-10-20表示训练完成并要求继续下一步；本轮据此核验当前训练、执行已完成单元的自身最佳 checkpoint Testing，并恢复原授权内尚未起训的单元。

## 完成结果

- Beauty200：训练 swu5s4wy，50k／500次验证／exit0，首次自身best49,900；Testing iyteug3c 正常结束。
- Beauty2026：训练 ppg0xyqx，50k／500次验证／exit0，首次自身best47,300；Testing vo7l74h3 正常结束。
- 两次Testing均在GPU1的独立tmux中经原intrr_inference.sh和src.main执行，单卡FP32、batch32、workers8、合法beam10，全量22,363用户。无用户、候选重复或非法SID；双writer一致，原始TFRecord按用户键独立复算四指标，最大绝对误差5.21e-17。两格训练、Testing及输出Artifact身份和lineage核验通过。
- Beauty42复用原hhaubm7t，重新核对原审计、预测hash及W&B finished／指标，无新增模型运行。Beauty三seed齐全，均值及样本std（ddof=1）由结构化指标计算；完整矩阵仅3/9。

## 队列阻断与恢复

实际并非九格全部训练完成：Sports42在起训前触发source changed守卫（exit126），其余五格因前驱停止（exit125），六格均无started_at和checkpoint。变化仅七份CoPMRec/BARS配置，IntRR模型、数据、入口及其TIGER协议依赖文件字节未变；61项聚焦配置／模型测试通过。Mutagen flush成功，三session Watching无冲突，当前本地／node1来源verified。

新来源f0082781575843db3af1d9f228f1e943a0d37fc8951694574b77c25478d324fc已单独核准，保留旧交接清单与六格原失败记录于各run目录的preflight-stop-20261020，更新六格unit的来源后恢复原tmux。原run ID、GPU4/5、50k、每100步验证、串行顺序均保持；不是模型训练重试。Sports42／dcgyc6s2已实际起训并核验至少1,700步，其余五格等待前驱。尚未完成Sports／Toys质量评测，不计算它们的seed汇总。

## 证据

- training-completion.json：两格完整验证历史、自身首次best、checkpoint SHA／contract、不可变Artifact与实际配置。
- testing-launch.json：两次Testing实际入口、run ID、GPU、端口和单元身份。
- audit_testing.py：零模型forward独立审计原始TFRecord、keyed bundle、源码归档、checkpoint、lineage和四指标。checkpoint_reference保存原URI，ckpt_path由launcher解析为本地缓存；审计核对实际缓存字节SHA与冻结checkpoint一致。
- beauty_s200-testing-audit.json、beauty_s2026-testing-audit.json：两格正式审计通过记录。
- beauty42-reuse.json：复用原已验收结果的本轮实时核验。
- beauty-three-seed-summary.json：三seed指标及mean／sample std，绑定输入审计文件SHA256。
- source-recovery.json、recovered-training-status.json：七配置差异、来源核准和六格恢复状态。

本轮新增2次正式Testing、0额外训练单元、0训练重试、0上游重跑。Sports／Toys六格沿用原400k训练预算。没有dry-run／5step临时运行，正式审计及实验材料保留在node1；JSON和逐用户材料按现有证据规则留本地，不默认纳入Git。
