## 1. 探查与基线

- [x] 1.1 检查工作树、CodeGraph、真实配置／根脚本及现有测试，确认命名影响与稳定身份边界。
- [x] 1.2 保存五个 experiment 和同一组 argv 的 resolved 配置基线及受保护代码／根脚本哈希。

## 2. 配置与验证

- [x] 2.1 新增两个轻量 BARS logger 组件，装配五个 experiment 的显示名及默认 group。
- [x] 2.2 扩展现有脚本／配置测试，验证默认命名、variant 身份、显式 group/name 覆盖、错误输入与 override 透传。
- [x] 2.3 比较迁移前后配置，完成 shell 语法、聚焦测试及严格 OpenSpec 验证，保存回执。
