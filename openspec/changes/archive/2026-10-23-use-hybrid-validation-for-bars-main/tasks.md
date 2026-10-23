## 1. 训练协议与默认配置

- [x] 1.1 增加显式选点模式、hybrid验证调用和checkpoint来源隔离，保留旧dense兼容。
- [x] 1.2 主版本component默认hybrid，checkpoint metadata记录选点来源。
- [x] 1.3 验证实际候选输出、恢复拒绝、真实脚本Hydra组合及strict规范。

## 2. 重启与验收

- [x] 2.1 停止旧dense八格队列并核验Beauty42实际选点模式，保存历史预算和产物。
- [x] 2.2 同步node1、核验冻结输入及九格配置、提交九格scratch训练，不自动Testing。
- [x] 2.3 核验首格实际hybrid Validation与checkpoint身份，更新Linear及研究状态并回读。
