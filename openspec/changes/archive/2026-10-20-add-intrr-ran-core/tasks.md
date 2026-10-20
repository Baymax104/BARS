## 1. 核心实现

- [x] 1.1 固定来源并实现独立 codebooks、层间递归、STE 与 teacher forcing。
- [x] 1.2 为输出、梯度、目标前缀隔离及非法输入编写最小 CPU 单测。

## 2. 验证

- [x] 2.1 从根目录运行聚焦单测并修复发现的问题。
- [x] 2.2 运行 OpenSpec strict 验证并记录完成状态。

验证：`uv run --no-sync pytest tests/recommendation/test_intrr_ran.py -q`（44 passed）；`uv run --no-sync ruff check` 聚焦文件通过；`openspec validate add-intrr-ran-core --strict` 通过。
