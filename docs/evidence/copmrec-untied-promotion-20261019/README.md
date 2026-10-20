# Untied主方法上位的文档与实验计划迁移回执

2026-10-19，用户明确决定Untied为当前BARS主方法、Shared保留对比。本次更新方法角色、研究状态、当前计划、相关方法/结果文档及Linear计划，不启动新增实验、不改已有run/checkpoint/Artifact身份。

## 当前主方法与覆盖

历史和目录分别使用P(c)+r_hist及P(c)+r_catalog，共享内容投影、独立商品残差；目录posterior用于前缀mass及最终排序。Untied完成Beauty42（g953gzcq/e4a3b038，BMX-184 Done），其余八格计划，Shared既有九格保留对比。原Shared三seed数字和消融不移贴到Untied。

主计划：[copmrec-untied-main-method-plan-20261019.md](../../../../research/docs/copmrec-untied-main-method-plan-20261019.md)；当前状态：[research-state.yaml](../../../../research/research-state.yaml)。普通根脚本仍Shared，Untied通过现有ablation入口显式variant运行，本次未宣称默认代码已切换。

## 新计划与授权

BMX-185为M2父项，186–193为8个Todo子项；Beauty42复用184。新主矩阵计划8×50k/400k+8Testing，实际执行0、未授权启动。已完成700k不改，若执行新主矩阵可见累计1100k。

BMX-194为零forward的M3准备，先审计旧no_residual复用；Untied no_joint_ce需独立组合实现/身份准备，至多1×50k+1Test为未采纳条件候选，不计400k。其他Shared辅助不机械重跑。

## 更新与验收

- 本地22份文档/当前导航核验，149个相对链接均存在，YAML无重复键；9个旧执行/研究状态块内容哈希保持，只有active scope更新并追加新决策块。
- Linear现有52对象更新且完整读回：项目1、文档4、里程碑5、M5 Todo41、BMX-184提示1；原122个issue状态不变。新增10个计划对象：主父项1+子项8+M3准备1，均Todo。
- 旧Shared四份论文PDF和原QA只绑定原构建；Untied方法/主表/参数/证据标签的稿件迁移列入M5，正文与PDF未在本次改写。
- git diff --check及原Untied OpenSpec strict通过。新训练/Testing/forward均0，没有归档提案或提交。

## 证据文件

[计划清单](promotion-plan.json)、[本地变更前块哈希](local-before.json)、[本地核验](local-verification.json)、[Linear旧对象写入审计](linear-write-audit.json)、[新增计划读回](linear-new-plan-readback.json)、[最终核验](final-verification.json)。原当前计划完整文本见[current-plan-before.md](current-plan-before.md)。
