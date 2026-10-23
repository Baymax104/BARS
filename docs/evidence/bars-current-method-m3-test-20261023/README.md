# 当前方法 M3：训练验收、独立Testing与贡献分析

日期：2026-10-23，北京时间。协议：`bars-fixed-half-hybrid-m3-20261023-v1`。当前状态：`completed_independently_accepted`。三训练150k、三次own-best Testing、C固定模型诊断及正式零forward贡献分析全部独立验收，正式结果3/3、剩余执行0。本轮新增训练0，不扩预算或扫描；下方13:24提交观察保留原时点。

## 最终验收与阶段决定

[三条Testing及Full来源独立审计](independent-testing-audit.json)全部通过：四来源各22,363完整真实用户、合法唯一Top10、两路径独立四指标复算、checkpoint／上游／源码／输出文件字节匹配，最大W&B指标误差5.90e-17。不可变预测URI/SHA与Artifact见[验收来源](independent-accepted-sources.json)。

正式CPU零forward贡献 `6cpl285w` finished／exit0；[完成回执](independent-contributions-completion.json)与[独立统计审计](independent-contributions-audit.json)通过4来源、89,452行用户CSV、4个bundle、12项配对区间、24项命中类别及守恒、全部文件MD5/SHA和lineage。实际发布 `bars_untied_beauty_seed42_contributions-analysis:v2`，digest `ee06a71c52403bf3bb20259d0754d2d3`，未混用历史v0。

Full／Shared／Zero／noCE的NDCG@10依次0.04527919／0.03857355／0.03586154／0.01040216。Full−Shared差+0.00670565，95%CI[0.00522777,0.00817414]，相对+17.38%；Full−Zero差+0.00941765，CI[0.00712597,0.01160523]，相对+26.26%；Full−noCE差+0.03487703，CI[0.03252653,0.03714077]，相对noCE提高335.29%，等价地noCE相对Full下降77.03%，两种百分比分母不同。全部12项组件指标用户区间为正。

按预定规则保留当前商品适配、Untied表示选择、唯一目录目标及C固定Full生成／同池排序用途，阶段收口，追加实验与预算0。用户区间只描述固定Beauty42来源，不推为跨训练seed稳健性；Shared不唯一识别梯度冲突，去CE没有mixture替代监督，A/B/C差额不相加为总收益分解。完整四指标、12项区间和贡献表、C结果及边界见[最终结果报告](../../bars-current-method-m3-results-20261023.md)。

本阶段实际完成3训练／150k、3次Testing、1次C固定模型分析及1次正式零forward贡献。原M3／M2等独立账本和启动／before-testing快照保持；本轮没有新增训练、模型重试、调参、上游、额外seed或论文修改。北京时间13:37:51的[Linear最终实时回读](linear-final-readback.json)确认205／194／206／207／208全部Done、M3里程碑100%，三个子项仍隶属205；M2父项185及九格仍全部Done。

## 本轮授权与历史边界

用户表示训练已完成并要求继续下一步，据此执行三个新臂各一次自身own-best Testing、独立结果验收及冻结预测贡献。仅Beauty／seed42，Full继续复用 `httwyhka → prt5r0v5`，不新增训练、重试、调参、seed／数据集、上游或独立Validation，不改论文与PDF。

旧M3三损失及750k账本、M2九格、[本阶段原启动快照](../bars-current-method-m3-20261023/README.md)均保持原身份。状态更新前五份研究文档原件与SHA保存在[before-testing](before-testing/manifest.json)，后续结果不得覆盖这些历史快照。具体问题、预测和正向／负向／uncertain决定规则沿用[原计划](../../bars-current-method-m3-plan-20261023.md)。

## 三训练与自身best验收

[training-audit.json](training-audit.json) 为 `all_passed`：三条真实W&B训练finished／exit0，完整50k、100次非空hybrid Validation、固定alpha0.5及对应目标、首次最高val/NDCG@10、不可变checkpoint发布文件MD5/SHA、optimizer、323份源码及冻结输入核验通过。

| 训练臂 | 实际train | 首次own-best step | best val/NDCG@10 | Testing提交身份 |
| --- | --- | ---: | ---: | --- |
| Shared，loss1/1/0 | `gu3l2s2s` | 47500 | 0.052285827696323395 | `e0m3cdsi` |
| 双侧零残差，loss1/1/0 | `1k2ebqaw` | 43500 | 0.045501478016376495 | `1ipsthvi` |
| Untied去Catalog CE，loss1/0/0 | `7u93dubs` | 45500 | 0.012618805281817913 | `srta7ooi` |

三条`last.ckpt`实际步数均等于各自own-best，不作为50k终点证据且未用于Testing。完整验证序列、终点console及exit0共同证实50k；保存状态观察不改变既定选点。原因未确定，不由此杜撰写入机制。

## C固定模型诊断独立验收

`gkwknl0l` finished／exit0；[mechanism-audit.json](mechanism-audit.json) 为passed。固定当前Full alpha0.5，22,363用户，production逐用户Top10精确复现 `prt5r0v5`；四臂合法唯一Top10、24项配对指标区间、生成／同池排序交互、贡献守恒、真实源码及Artifact字节均通过独立核验，审计新增forward为0。详细已验收C结果见[mechanism-results.md](mechanism-results.md)。

C是固定模型推理干预，0训练更新；它不代替新组件训练臂结果，不将A/B/C差值相加为总收益分解，不把用户区间解释为训练seed稳健性。三条正式Testing与配对贡献现也全部独立验收，整个M3阶段已收口。

## Testing提交与13:24进程观察（历史时点）

13:22:59提交三组独立tmux，GPU0、单卡FP32、Shared→Zero→noCE单队列，均使用各自不可变own-best URI/SHA，失败停止、不重试。远端批次：`/data3/weizhenyu/projects/GRID/logs/copmrec_v2/m3_current_test_20261023_132144`。真实命令、checkpoint及预留run见[testing-plan.json](testing-plan.json)，预检见[prepare.json](prepare.json)，提交见[submit.json](submit.json)。

| 条件 | Testing身份 | tmux | 13:24:32进程观察 |
| --- | --- | --- | --- |
| Shared | `e0m3cdsi` | `bmx-206-m3-shared-test-20261023_132144` | running，结果待验收 |
| Zero | `1ipsthvi` | `bmx-206-m3-zero-test-20261023_132144` | queued |
| noCE | `srta7ooi` | `bmx-207-m3-noce-test-20261023_132144` | queued |

上表保留13:24:32的历史进程观察；[status.json](status.json)现已更新为最终状态回执，不将其称为该时点原快照。提交与排队本身不计独立验收，三条任务后续实际执行与四指标、预测URI/SHA、全量真实用户、lineage及独立TFRecord复算通过情况见顶部最终审计。

## 13:24待验收登记（历史时点，已由顶部最终验收取代）

本阶段训练实际完成3／150k，本轮新增训练0。Testing授权3／提交3／当前已独立验收0；C分析完成1／独立验收1；冻结预测贡献待新预测。Testing结束后按真实key对齐Full与三个新臂，独立复算四指标、PCG64 seed42／2000次用户配对区间及命中贡献守恒，再按原预定结果规则决定保留／收缩／uncertain；无自动扫描或额外预算。

上述13:24登记反映当时仍在进行的执行，不作为当前状态；顶部最终验收及结果报告已由后续真实审计更新。最终组件判断使用正式Testing和配对贡献，不用Validation差异代替。
