"""新数据集文本读取的编码适配，不改变既有预处理默认行为。"""

import numpy as np


def decode_utf8_features(
    row: dict[str, np.ndarray],
    features_to_apply: list[str] | None = None,
) -> dict[str, np.ndarray]:
    """严格解码 UTF-8 字节，保留文本数组形状及未选中的特征。"""
    for name, value in row.items():
        if features_to_apply and name not in features_to_apply:
            continue
        array = np.asarray(value)
        decoded = []
        for text in array.flat:
            if isinstance(text, bytes):
                decoded.append(text.decode("utf-8"))
            elif isinstance(text, str):
                decoded.append(text)
            else:
                raise TypeError(f"Expected text bytes or string in feature {name!r}, got {type(text).__name__}.")
        row[name] = np.asarray(decoded, dtype=str).reshape(array.shape)
    return row
