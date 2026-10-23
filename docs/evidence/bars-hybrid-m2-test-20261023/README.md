# BARS M2：hybrid选点九格训练验收与正式Testing

## 本轮授权与范围

用户于2026-10-23表示已完成全部训练并要求继续下一步。本轮执行九格各一次自身own-best hybrid Testing及独立验收；0新增训练、调参、独立Validation、上游、额外seed或自动重试。此前训练阶段不自动Testing的限制保留原时点含义。

## 训练验收

九格均finished／exit0、50,000更新／100次hybrid Validation。使用W&B精确scan_history读取全部100个非空val/ndcg@10记录，按更新数升序首次最高点选择；与已保存checkpoint、发布Artifact及完整契约一致。323份源码与训练冻结版本一致，SHA256为`cc2a911330f089f71e63916616f05859da976d3699dd7a1e42c219b25eceda6a`。每格完整检查见[training-audit.json](training-audit.json)。

| Linear | 数据集 | seed | train | own-best step | best val/NDCG@10 | Testing |
| --- | --- | ---: | --- | ---: | ---: | --- |
| BMX-209 | beauty | 42 | httwyhka | 46000 | 0.0589281544 | prt5r0v5 |
| BMX-186 | beauty | 200 | 63whsx9s | 50000 | 0.0590232983 | ucwg1gx8 |
| BMX-187 | beauty | 2026 | uotmewdu | 39500 | 0.0589112416 | cv4u0qra |
| BMX-188 | sports | 42 | op60l871 | 43000 | 0.0328004546 | 7ifxazq1 |
| BMX-189 | sports | 200 | ubr7izg9 | 49000 | 0.0320980102 | 37b2swvn |
| BMX-190 | sports | 2026 | 4c00jwid | 43000 | 0.0325302407 | dzya58si |
| BMX-191 | toys | 42 | 0yi4zt92 | 47500 | 0.0636198148 | ravv9510 |
| BMX-192 | toys | 200 | 576pc4tq | 40500 | 0.0639027134 | acx4bn8h |
| BMX-193 | toys | 2026 | wis7tks0 | 41500 | 0.0640453324 | 6vec0x7h |

## 正式Testing

北京时间2026-10-23 01:41:07已提交九个独立tmux，node1物理GPU4、逻辑[0]、FP32单进程串行。每格使用不可变v0 checkpoint URI与SHA，根脚本`copmrec_ablation_inference.sh`进入统一`src.main`。前驱exit0、源码一致、GPU连续三次利用率低于10%且显存余量至少16GiB后继续；失败停止，不重试、不终止已有服务。

固定alpha=0.5、Untied双残差、训练loss1/1/0保持。候选为混合概率beam20并入全部cold；joint catalog logits按catalog row稳定Top10，无历史排除；真实evaluation/validation_selection/prediction三者均hybrid。每格从自身首次最高hybrid Validation恢复。

Mutagen首次flush遇daemon重连未就绪，连接后通过统一入口再次flush成功，三个session均Watching；无代码行为改动。1818份冻结TFRecord及六份上游Artifact、目录和seen-mask通过逐文件校验；606份testing分片另行检查。九格真实root-script argv、Hydra compose与bash语法通过，预检0模型forward。

初次preflight已在远端成功完成，但上游reader进度输出导致本地JSON解析报错；已修正回执解析并从原stdout恢复prepare.json，没有重复准备或运行模型。

回执：[testing-plan.json](testing-plan.json)、[prepare.json](prepare.json)、[submit.json](submit.json)、[status.json](status.json)。远端批次：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m2_hybrid_test_20261023_013814`。

## 独立验收口径

Testing finished／exit0后，核对全量真实testing用户、唯一合法Top10、checkpoint与SID/embedding lineage、预测Artifact文件MD5/SHA256及源码归档。读取冻结原始TFRecord提取最终item标签，以标准model output bundle中的SID预测独立复算R@5、N@5、R@10、N@10，再用逐行tuple rank和math.fsum第二路径交叉验证；与W&B差须低于1e-12。按数据集汇总三训练seed的mean与样本std（ddof=1），不混合数据集。

当前完成状态以最新status与testing-audit观察时间为准；提交和退出0不单独作为完整结果。旧dense实验与旧三损失M3证据保持原来源边界。

## 最终验收

九格Testing全部finished／exit0并通过独立验收，当前主矩阵9/9。四指标与W&B最大绝对误差为`6.2450045135165055e-17`。逐格checkpoint/output URI、SHA、Artifact digest、完整用户与源码证据见[testing-audit.json](testing-audit.json)，三seed汇总见[正式结果](../../bars-hybrid-m2-results-20261023.md)。本批450k训练与9Testing完成；本轮0新增训练、上游、调参或模型重试。研究状态和Linear按当前结果同步，论文文件未修改。
