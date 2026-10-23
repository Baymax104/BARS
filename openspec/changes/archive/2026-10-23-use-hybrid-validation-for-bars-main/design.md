## Context

ScratchTrainingProtocol既限制evaluation_mode=dense，又在eval_step显式调用dense retrieve。单改Hydra字段无法切换选点。既有checkpoint的copmrec_unified_scratch要求完整字典相等，必须保留旧dense身份并为新hybrid明确建立新身份。

## Goals / Non-Goals

目标：主版本hybrid Validation与推荐共用已有retrieve候选流程；保持50k、500步间隔、DDP2/global256/FP32和1/1/0目标；九格从零重启。范围外：新模型机制、调参、上游重跑和自动Testing。

## Decisions

- 增加独立的validation_selection_mode，默认dense以保留旧checkpoint路径；evaluation_mode必须与它一致，eval_step按该模式调用现有Liger.retrieve。
- hybrid checkpoint契约增加候选配置，dense契约保持原字节语义；跨选点模式、候选配置不一致时拒绝恢复。推理配置保留同一选择身份，不以prediction_mode反推旧来源。
- component按variant映射选择模式，只有当前主版本默认hybrid；其他变体不变。checkpoint writer显式记录选择模式。
- 旧八格队列先从尾部停止并核验进程退出，再同步和提交新九格；Beauty42实际dense配置作为必须重训的依据。
- 新队列使用当前低利用率、显存充足的GPU4/5，逐格源码/资源守卫、独立身份、前驱exit0后继续。

## Risks / Trade-offs

- hybrid验证成本更高：沿用用户指定100次Validation和预算，不额外独立验证。
- 旧结果误填主表：新矩阵覆盖清零，旧Beauty42和中止训练只作历史账本。
- 推理加载dense来源时，新默认hybrid会拒绝：历史复验显式选择dense身份，禁止静默重标。
