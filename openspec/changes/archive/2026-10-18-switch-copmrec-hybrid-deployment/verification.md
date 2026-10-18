# 实现验证

## 模型与既有训练身份

执行于 Windows 本地仓库根目录：

```powershell
uv run --no-sync pytest tests/recommendation/test_copmrec_v2.py tests/recommendation/test_copmrec_hybrid.py tests/recommendation/test_copmrec_fixed_alpha.py tests/recommendation/test_liger_probability_mixture.py -q
```

结果：86 passed。覆盖五种训练身份的旧 dense own-best 到两种部署模式的严格恢复、拒绝重标训练契约、history/cold 合法性、beam候选去重与稳定 ties、无额外 seen dense 补入、Validation 恒为 dense、各候选 alpha 策略。

```powershell
uv run --no-sync ruff check src/recommendation/copmrec/module.py src/recommendation/copmrec/protocol.py tests/recommendation/test_copmrec_hybrid.py tests/recommendation/test_copmrec_v2.py
openspec validate switch-copmrec-hybrid-deployment --strict
```

结果：Ruff check 与 OpenSpec strict 通过；protocol.py 已经 Ruff 格式化。上述86项为模型子集，以下登记完整集成验证。

## 配置、脚本与产物协议集成验证

```powershell
uv run --no-sync pytest tests/recommendation/test_copmrec_v2.py tests/recommendation/test_copmrec_hybrid.py tests/recommendation/test_copmrec_fixed_alpha.py tests/recommendation/test_liger_probability_mixture.py tests/test_copmrec_v2_config_script.py tests/data/components/test_m3_prediction_deployment.py tests/data/components/test_artifacts.py -q
```

结果：177 passed，4条依赖deprecation warnings，24.29秒。包括Hydra compose、默认hybrid/显式dense、实际模型mode元信息、脚本语法/quoting/空值/错误输入/额外override、hybrid hits输入身份门禁及旧dense辅助兼容。相关修改文件Ruff和`git diff --check`通过。详见`docs/evidence/copmrec-hybrid-migration-20261018/validation.json`。

Mutagen flush后三session均Watching for changes且无conflict。正式源码SHA256为`154f2ae8e76c30b49209d16cbfbea338713367ec742ee623f452b585809ab3e9`；298个运行归档文件均逐项匹配本地origin。Full Beauty42 `64mjlgze`和fixed_alpha_one `92gwx86m`两格gate独立通过，有效alpha分别为0.9887976050376892和精确1；最大四指标复算误差3.47e-17。

2026-10-18 06:33:54 UTC，13次正式推理均exit0、真实run ID和结束时间齐全；全13最终独立审计passed，最大四指标误差6.245e-17。BMX-183 `ppjhagjq`于06:46:55 UTC结束exit0且最终hits审计passed：22363用户/89452记录，四正式hybrid bundle、分解守恒、案例/切片/CI均核验，切片均值与配对CI复算误差0，实际分析及审计forward均0。

13/13推理与1/1零forward分析已结案；0新增训练/独立Validation，650k训练成本及旧证据保留。17个新增Linear任务均Done/有效，原104项状态保持，41个M5写作计划仍Todo。研究YAML、14真实来源、两端plan、结果/URI/CI与原state块字节保护检查通过。完整证据见`docs/evidence/copmrec-hybrid-migration-20261018/README.md`及final执行/审计/Linear/research核验回执。
