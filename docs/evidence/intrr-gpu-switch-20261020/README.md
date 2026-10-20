# IntRR 后续队列使用 GPU4/5

用户在2026-10-20明确允许使用其他有多余显存的GPU。现场GPU4/5各空闲49,401MiB，连续三次pmon的计算利用率为0%；两卡有常驻vLLM服务，允许共享其剩余显存，不停止已有服务。

## 执行

先将现有交接清单临时置为resource_migration，确认七格均无started_at记录。仅停止七格等待中的tmux控制pane，保留log pane和session；没有停止或重启模型训练。为现有wrapper更新CUDA_VISIBLE_DEVICES=4,5及W&B的execution_physical_gpu_ids=[4,5]，其余命令、run ID、端口、前驱和模型协议保持。七格改用同一个serial-training.lock，仍最多运行一个IntRR双卡训练。

运行guard检查所选GPU4/5各空闲至少20,480MiB，按本次明确授权允许其他用户服务共用；数据逐文件哈希、来源verified、端口、磁盘和前驱成功检查继续保留。修改后的全部wrapper通过bash -n，guard通过语法检查并实际预检成功。旧guard、wrapper、unit.json及交接清单的副本保存在原node1批次目录和各run目录。

02:05左右完成切换，Beauty2026／BMX-198／ppg0xyqx在原tmux `bmx-198-intrr-beauty2026-20261019_224718`启动；两个rank PID4005135／4005136分别位于GPU4／5，CUDA_VISIBLE_DEVICES=4,5。W&B实际配置确认history-encoding-reuse-v1、DDP2、逻辑devices=[0,1]、50k、每100步验证、关闭自动Testing；源码SHA256仍为2447de596b5742ac3445fdac04f171b2b20bed0401098bb4c3eb12c5e3d98b07，来源verified。后六格等待各自前驱。

## 证据

- `startup-audit.json`：实际W&B配置、源码身份、GPU与双rank进程、八格队列状态、资源切换清单。
- `progress-audit.json`：已核验实际W&B running、零基步数699（已记录700步），两个rank继续位于GPU4/5，模型版本及源码身份正确；console已观察到前500步的5次Validation与best checkpoint保存。

本次为现有已授权队列资源调整，新增训练格、训练重试、Testing均为0。共享设备的后续计算负载可能变化，不据启动采样承诺训练提速倍数。
