"""独立原始数据准备；不参与模型运行时装配。"""

from src.data.preparation.pipeline import PreparationConfig, prepare_dataset

__all__ = ["PreparationConfig", "prepare_dataset"]
