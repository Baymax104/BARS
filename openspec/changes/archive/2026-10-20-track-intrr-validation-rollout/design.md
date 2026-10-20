## Context

模型模块优化已通过 74 项测试。当前首格还在训练，另外七格由 tmux wrapper 按前驱 exit_code 串行调度。原 guard 使用原 preflight 的固定源码哈希。

## Goals / Non-Goals

目标：首格保持原实现自然结束，后继七格使用已验证版本，并保留新旧身份。范围外：训练预算、Testing、新实验格及 GPU 调度策略。

## Decisions

暂停三个 Mutagen session 后编辑本地代码。先给现有 guard 增加 preparing 等待条件，保存旧 guard；原 preflight 不覆盖。首格 exit_code=0 后 resume、flush、status 核验，再以原子替换方式写 ready 交接清单与新 source_sha256。guard 检查 ready、首格成功、新来源 verified 后继续原数据、GPU、端口检查。

训练 experiment 的 `validation_implementation` 为实现元数据；不传入模型构造参数，也不改变 checkpoint 契约。既有 wrapper 从配置读取该字段，无需编辑正在等待的 bash 脚本。

## Risks / Trade-offs

资源不满足时继续等待，不终止其他用户进程。首格异常或同步失败时保持 preparing 并保留错误证据；不得自动将失败当作成功放行。版本切换后不再修改受管源代码，避免后继哈希检查失败。
