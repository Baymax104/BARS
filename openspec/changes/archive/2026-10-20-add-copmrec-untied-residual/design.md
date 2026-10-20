## Context

当前 BARS 使用一张零初始化商品残差表。LIGER 的 encode 和 dense_logits 均调用 item_content_residual；CoPMRec 的 optimizer、scratch 零初值及 cold checkpoint 校验也假设单表。已有 Full、原三臂和 fixed_alpha_one 具有严格历史身份，必须继续可恢复。

## Goals / Non-Goals

目标是通过现有消融入口准备 Shared/Untied 的直接重训比较，保持公共初始化、三目标、两表学习率、own-best 选择和 hybrid 部署可匹配。范围固定 Beauty seed42，一次50k scratch训练和一次自身单卡Testing；本轮不运行它们。

不加入 history-only/catalog-only、alpha扫描、参数量配平、额外dense Testing或机制run；不重写旧checkpoint或改动原四bundle诊断集合。

## Decisions

1. LIGER 增加历史残差 hook，默认委托现有商品残差 hook。仅 encode 改调用历史 hook，dense_logits 继续现有 hook，保留所有旧共享行为与诊断干预。
2. `CoPMRecAblation(variant=untied_residual)` 保留 collaborative_residual 为目录表，新增 history_collaborative_residual 作为历史表；两者用零 Tensor 建立独立 Embedding，不消耗 RNG。共享 content_projection 和其余网络，均使用 seen mask、scale=1。
3. 残差层维护确定顺序的残差参数名称集合。实际 optimizer、严格 optimizer 参数组、scratch 零初值及cold checkpoint检查统一读取该集合。两表置于同一 residual 参数组，LR=0.002；base LR=0.0003，wd=0.035，warm2500/cosine50000不变。旧shared参数顺序与契约字典保持原值。
4. 新臂通过 variant、untied residual protocol、sharing模式和双表state获得独立checkpoint身份。完整保留各自AdamW moments与scheduler，拒绝跨变体、缺表、缺moment、错误组及cold非零状态；不得复制已训练Full冒充scratch。
5. 扩展TRAINING_VARIANTS和现有配置/根脚本白名单，保持原VARIANTS三臂与四bundle诊断不变。结构化配置及writer元数据登记共享模式、表数、三目标和alpha策略。
6. 固定数据/SID/content/catalog/seen-mask指纹；同seed公共参数及初始dropout RNG必须逐项匹配Full。训练DDP2/global256/FP32/50k，每500步dense Validation，以自身首次最高val/NDCG@10选点；Testing使用mixture beam20+allcold+joint logits候选内stable Top10，全阶段无历史排除。
7. 在研究文档及状态登记新补充为prepared_not_started，run/checkpoint/指标留空。保留650k既有花费和已闭环hybrid13+1，新增计划50k不代表执行授权；不修改主方法选择。

## Risks / Trade-offs

- 新表误入基础LR组或未被checkpoint校验覆盖 → 共享参数集合和真实CPU优化/恢复测试覆盖两表。
- 新表构造改变公共初始化或dropout随机数 → 同seed state及RNG精确对照，初始各loss一致、shared梯度等于双侧梯度和。
- Untied残差参数从128N增至256N → 登记实际参数增量；不唯一归因于一致性、容量、正则化或梯度耦合，不额外调LR/wd。
- 单seed证据范围有限 → 结论限定Beauty42；跨seed稳定性需运行前另定固定预算，不按Testing方向追加。

## Migration Plan

先本地CPU测试、Hydra compose、Bash语法与参数、Ruff和OpenSpec strict，再交付手动训练/Testing命令。此次不操作远端或启动实验；未来交给node1前按项目约定Mutagen flush。旧训练契约无需迁移。
