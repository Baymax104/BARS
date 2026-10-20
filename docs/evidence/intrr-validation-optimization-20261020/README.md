# IntRR 验证优化证据

后续状态更新：用户授权使用其他GPU的多余显存后，02:05左右七格切换至GPU4/5，Beauty2026已实际起训并核验至少700步；其余六格等待前驱。见[资源切换证据](../intrr-gpu-switch-20261020/README.md)。下方GPU0等待描述和after-handover.json均保留原交接时点含义。

- `before-handover.json`：同步暂停后的远端来源、320 文件哈希、首格运行状态及 preparing 清单。
- `complete-handover.ps1`：本批次的一次性交接操作，等待当前训练成功后同步并放行原队列。
- `verification.json`：141项测试、等价范围和仅两份运行源码变化。
- `handover.json`：已成功写入的 ready 清单，绑定新源码与可信本地来源、七格身份及原preflight摘要。
- `after-handover.json`：切换后另行回读的队列状态、实际源码与首格完成证据。
- `training-completion.json`：W&B完整500次验证、finished、首次最高val step49,900与本地checkpoint step／SHA核准，新增模型forward为0。

01:44:50（北京时间）完成新版本交接。当前原首格训练完成待Testing；第二格Beauty2026等待GPU0其他用户进程，其余六格等待前驱，所有tmux正常。资源满足后队列自动继续；未将等待状态记作实际训练。

本轮模型 74 项、配置/数据 67 项聚焦 CPU 测试通过；两个 OpenSpec strict 通过。正式运行预算和 Testing 范围保持，不产生额外 GPU 检查运行。
