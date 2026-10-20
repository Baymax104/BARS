## 1. 规格与实验边界

- [x] 1.1 固定Untied变体、Beauty42唯一新增单元、既有Full来源及50k计划，完成proposal/design/specs。

## 2. 模型实现

- [x] 2.1 增加历史残差hook与独立零初始化history表，保持公共初值及旧shared路径。
- [x] 2.2 统一双表optimizer参数组、scratch零初值及cold状态校验，补齐独立checkpoint身份与完整恢复。

## 3. 配置、入口与研究登记

- [x] 3.1 扩展现有消融配置和根脚本，新臂共享模式/表数/alpha元数据可核验，旧四bundle诊断不扩展。
- [x] 3.2 登记中文实验计划及research-state/current-plan，run/checkpoint/指标保持未执行，提供手动命令。

## 4. 验证

- [x] 4.1 通过真实CPU小模型的初值/RNG、双侧梯度、cold及optimizer/checkpoint严格恢复测试。
- [x] 4.2 通过旧变体回归、Hydra compose、脚本语法/quoting/空值/错误输入/override、Ruff、diff和OpenSpec strict，保留验证回执。
