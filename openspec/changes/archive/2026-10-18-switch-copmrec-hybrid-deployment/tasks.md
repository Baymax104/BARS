## 1. 规格与训练身份

- [x] 1.1 建立 hybrid 部署与旧训练身份分离的 proposal、design 和 delta specs，冻结零新增训练及13次推理/1次hits范围。
- [x] 1.2 放开 hybrid prediction 并保留 dense Validation，严格兼容旧 v2 own-best，不改写旧 checkpoint 契约。

## 2. 模型与配置

- [x] 2.1 实现 hybrid/dense 检索分派、独立 deployment/eligibility 契约，保留各臂正确候选 alpha。
- [x] 2.2 对齐 Full/消融配置、脚本与产物 metadata；显式 dense override 正确改变运行标签。
- [x] 2.3 hits 校验四份 hybrid 产物的协议，residual/prefix 保留 dense 身份。

## 3. 验证

- [x] 3.1 CPU 单测覆盖旧 own-best 恢复、两模式、candidate/cold union、稳定 ties、历史资格、alpha策略及 dense Validation。
- [x] 3.2 通过相关配置 compose、脚本语法/参数测试、Ruff 与 OpenSpec strict，并保留验证记录。

## 4. 正式执行与登记

- [x] 4.1 更新研究与 Linear 计划，区分已完成训练、旧dense、临时hybrid及本次正式矩阵；新增训练为零。
- [x] 4.2 flush 并确认三个 Mutagen session 无冲突；在 node1 tmux 使用统一入口执行13次推理及1次hits。
- [x] 4.3 核验 W&B、checkpoint SHA、源码、输入及 keyed 产物，登记实际完成矩阵和比较，不将启动视为完成。
