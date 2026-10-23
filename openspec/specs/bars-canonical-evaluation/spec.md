# bars-canonical-evaluation Specification

## Purpose
定义 BARS 公共 hybrid 推荐入口、显示规则与来源引用。17条 dense run 清理是已执行的一次性历史迁移，不授权再次删除；Beauty42 当前 hybrid 选点来源见 M2 验收。

## Requirements
### Requirement: BARS 唯一推荐测试入口

公共BARS推理脚本 SHALL 默认使用hybrid，显示名称使用test或validation而不包含hybrid/dense分类，保留数据集、seed和变体。

#### Scenario: 默认测试
- **WHEN** 用户未提供deployment参数运行BARS测试
- **THEN** 实际部署是hybrid、显示名以test结尾，训练验证协议不变

#### Scenario: 旧dense参数
- **WHEN** 公共脚本收到 dense 部署参数或将 prediction_mode 改为非 hybrid 的 override
- **THEN** 明确拒绝该请求且不启动模型，其他合法override继续支持

### Requirement: 指定dense记录清理

系统 SHALL 删除17条已核验的BARS独立dense测试run，不删除其独立Artifact、任何训练记录或其他方法run。

#### Scenario: 批量删除验收
- **WHEN** 完成用户授权的dense记录清理
- **THEN** 17个run ID从项目消失，保留run配置/指标及独立Artifact内容均不变

### Requirement: 当前引用一致

系统 SHALL 更新Linear和当前研究记录中的测试命名及命令，删除run只作为明确历史事实保留。

#### Scenario: 当前主结果
- **WHEN** 查看新BARS Beauty42主结果
- **THEN** 当前 hybrid 选点主矩阵引用已验收的 prt5r0v5；3rthtvc4 保留其此前来源时点，tf18g4ec 标为已删除历史记录且不作为当前入口
