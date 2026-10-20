## 1. 正式入口

- [x] 1.1 新增继承TIGER的数据、模型及薄experiment配置。
- [x] 1.2 新增统一train/inference根脚本和中文使用说明。

## 2. 本地验证

- [x] 2.1 完成轻量compose深比较、脚本quoting/错误输入/override与语法检查。
- [x] 2.2 运行聚焦集成回归、lint及OpenSpec strict验证。

## 3. node1有界验证

- [x] 3.1 Mutagen同步并核对三会话无conflict。
- [x] 3.2 执行dry-run和最多5step训练、有限预测与checkpoint恢复核验。
- [x] 3.3 清理本次临时运行记录/审计文件/tmux并确认，不启动正式训练。

本地聚焦回归152项通过，包含38项配置/真实脚本测试；相关lint和三个提案strict验证通过。node1使用现有环境完成单卡dry-run 1step、双卡5step及单批预测；checkpoint global_step与全部Adam step均为5、浮点状态有限。自身validation checkpoint成功恢复，公共writer输出32条、每条10个合法且唯一的4层SID，退出码均0。外部logger/发布关闭；本次远端临时运行目录及tmux、本地作者源码/对照脚本临时目录已删除并核对不存在。保留代码、单测、提案和使用说明，未启动正式50k。
