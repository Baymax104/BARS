# IntRR 训练速度诊断证据

诊断结论和适用边界见[耗时报告](../../intrr-speed-diagnosis-20261020.md)。本目录仅记录零模型forward的性能排查，训练继续使用原协议。

- `oipt22mb-history.json`、`swu5s4wy-history.json`：两个明确run的完整阶段日志，仅选择时间、step和loss／validation字段。
- `timing-series.json`：50步纯训练、单次validation及100步完整周期的逐事件计时。
- `timing-audit.json`：阶段统计及同进度窗口比较。
- `resource-and-config-audit.json`：进程UID、GPU活动样本和实际W&B配置对比，不包含认证信息。
- `source-comparison.json`：16份实际运行源码／协议文件的SHA256一致性核对。
- `collect_timing.py`：读取指定W&B run或缓存历史的可复核耗时检测器；不加载模型或Trainer。
- `timing-replay.json`：真实历史重放结果；近期周期告警阈值为旧run的1.5倍。

原始审计副本保存在node1 `logs/intrr/performance_diagnosis_20261020/`；本地JSON按项目证据规则保留，默认不纳入Git。没有追加训练、Testing、模型重放或CUDA profiler，也没有向现有正式run注入调试日志。
