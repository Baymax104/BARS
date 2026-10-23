# BARS M2：hybrid Validation主矩阵正式结果（2026-10-23）

## 结果与范围

当前主方法 `untied_fixed_alpha_half_no_mixture` 的 Beauty／Sports／Toys × seed42／200／2026 共九格已全部验收。每格50,000次scratch更新、100次hybrid Validation，按自身首次最高val/NDCG@10选点；本轮用户要求继续下一步后，分别执行唯一一次自身own-best Testing。九次Testing均W&B finished／exit0，完整预测及四指标通过原始TFRecord独立复算。

模型固定alpha=0.5，SID CE／Catalog CE／mixture NLL权重1／1／0，history/catalog residual独立、内容投影共享。Validation与Testing均为概率混合beam20并入全部cold，以joint catalog logits按catalog row稳定Top10，无历史排除。训练验证loss的全目录分母不改变hybrid排名选点身份。

## 三个训练seed汇总

下表为原始比例的 mean ± sample std，样本标准差ddof=1；每行仅汇总同一数据集三个训练seed。

| 数据集 | 用户数/格 | Recall@5 | NDCG@5 | Recall@10 | NDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| beauty | 22363 | 0.05373459 ± 0.00054093 | 0.03832172 ± 0.00030532 | 0.07522843 ± 0.00026202 | 0.04523814 ± 0.00020087 |
| sports | 35598 | 0.02794164 ± 0.00047535 | 0.01894777 ± 0.00029355 | 0.04241811 ± 0.00032397 | 0.02359542 ± 0.00024897 |
| toys | 19412 | 0.05948211 ± 0.00012964 | 0.04376807 ± 0.00043257 | 0.08106669 ± 0.00038665 | 0.05071054 ± 0.00055179 |

## 逐格结果与来源

| Linear | 数据集/seed | train | best step | Testing | R@5 | N@5 | R@10 | N@10 |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| [BMX-209](https://linear.app/baymax104/issue/BMX-209) | beauty/42 | [httwyhka](https://wandb.ai/baymaxam/GRID/runs/httwyhka) | 46000 | [prt5r0v5](https://wandb.ai/baymaxam/GRID/runs/prt5r0v5) | 0.0539283638 | 0.0384278899 | 0.0751240889 | 0.0452791938 |
| [BMX-186](https://linear.app/baymax104/issue/BMX-186) | beauty/200 | [63whsx9s](https://wandb.ai/baymaxam/GRID/runs/63whsx9s) | 50000 | [ucwg1gx8](https://wandb.ai/baymaxam/GRID/runs/ucwg1gx8) | 0.0531234629 | 0.0379774866 | 0.0750346555 | 0.0450199070 |
| [BMX-187](https://linear.app/baymax104/issue/BMX-187) | beauty/2026 | [uotmewdu](https://wandb.ai/baymaxam/GRID/runs/uotmewdu) | 39500 | [cv4u0qra](https://wandb.ai/baymaxam/GRID/runs/cv4u0qra) | 0.0541519474 | 0.0385597907 | 0.0755265394 | 0.0454153080 |
| [BMX-188](https://linear.app/baymax104/issue/BMX-188) | sports/42 | [op60l871](https://wandb.ai/baymaxam/GRID/runs/op60l871) | 43000 | [7ifxazq1](https://wandb.ai/baymaxam/GRID/runs/7ifxazq1) | 0.0283442890 | 0.0192607555 | 0.0427833024 | 0.0238799132 |
| [BMX-189](https://linear.app/baymax104/issue/BMX-189) | sports/200 | [ubr7izg9](https://wandb.ai/baymaxam/GRID/runs/ubr7izg9) | 49000 | [37b2swvn](https://wandb.ai/baymaxam/GRID/runs/37b2swvn) | 0.0274172706 | 0.0186785691 | 0.0423057475 | 0.0234890318 |
| [BMX-190](https://linear.app/baymax104/issue/BMX-190) | sports/2026 | [4c00jwid](https://wandb.ai/baymaxam/GRID/runs/4c00jwid) | 43000 | [dzya58si](https://wandb.ai/baymaxam/GRID/runs/dzya58si) | 0.0280633743 | 0.0189039831 | 0.0421652902 | 0.0234173200 |
| [BMX-191](https://linear.app/baymax104/issue/BMX-191) | toys/42 | [0yi4zt92](https://wandb.ai/baymaxam/GRID/runs/0yi4zt92) | 47500 | [ravv9510](https://wandb.ai/baymaxam/GRID/runs/ravv9510) | 0.0593447352 | 0.0433791873 | 0.0806717494 | 0.0502013776 |
| [BMX-192](https://linear.app/baymax104/issue/BMX-192) | toys/200 | [576pc4tq](https://wandb.ai/baymaxam/GRID/runs/576pc4tq) | 40500 | [acx4bn8h](https://wandb.ai/baymaxam/GRID/runs/acx4bn8h) | 0.0594992788 | 0.0442339754 | 0.0814444673 | 0.0512968323 |
| [BMX-193](https://linear.app/baymax104/issue/BMX-193) | toys/2026 | [wis7tks0](https://wandb.ai/baymaxam/GRID/runs/wis7tks0) | 41500 | [6vec0x7h](https://wandb.ai/baymaxam/GRID/runs/6vec0x7h) | 0.0596023079 | 0.0436910415 | 0.0810838657 | 0.0506334061 |

## 独立验收

- Beauty每格22,363用户，Sports每格35,598用户，Toys每格19,412用户；标准bundle形状分别为[N,10,4]，所有真实用户完整匹配，Top10合法且无重复。
- 读取冻结原始TFRecord的最终商品标签，独立计算Recall/NDCG@5/10；另以逐行tuple rank和math.fsum交叉验证。与W&B四指标最大绝对误差为 `6.2450045135165055e-17`。
- 每格的checkpoint URI固定v0，实际消费文件SHA与自身训练首次最高点一致；SID/embedding输入与checkpoint/output Artifact lineage、MD5/SHA、源码archive及manifest均核验通过。
- 323份源码SHA保持 `cc2a911330f089f71e63916616f05859da976d3699dd7a1e42c219b25eceda6a`；1818份TFRecord与冻结输入逐文件一致，实际root-script Hydra compose与bash语法通过。没有为审计执行模型forward。

## 预算与证据边界

新hybrid协议批次共9训练／450k更新＋9次Testing，当前完整覆盖9/9，剩余训练与Testing为0。本轮只执行9次Testing，新增训练、独立Validation、额外seed、smoke、调参、上游和模型重试均为0。旧dense run、原Beauty42结果和已耗历史成本完整保留，不混入当前矩阵。旧三损失M3仍只证明其原模型，不改写为当前两损失模型的机制实证。

新结果已满足当前hybrid选点主矩阵的数据资格。本轮同步结果与研究状态，论文数值和既有PDF未改动；因此此前PDF的P-SELECT占位仍需后续稿件更新，不声称主表已经填入。

结构化来源：[训练验收](evidence/bars-hybrid-m2-test-20261023/training-audit.json)、[完整Testing验收](evidence/bars-hybrid-m2-test-20261023/testing-audit.json)、[运行计划](evidence/bars-hybrid-m2-test-20261023/testing-plan.json)、[执行与验收说明](evidence/bars-hybrid-m2-test-20261023/README.md)。
