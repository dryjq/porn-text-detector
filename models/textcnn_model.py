"""TextCNN 模型占位实现。

实际项目可替换为训练好的 PyTorch TextCNN 模型，这里提供可运行的简化版本。
"""
from typing import Tuple
import random

try:
    import torch  # type: ignore
    import torch.nn as nn  # type: ignore
except Exception:  # noqa: BLE001
    torch = None
    nn = None

from models import BaseTextClassifier


class TextCNNClassifier(BaseTextClassifier):
    name = "textcnn"

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path

    def load_model(self) -> None:
        # 为便于演示，未加载真实权重
        self.is_loaded = True

    def predict(self, text: str) -> int:
        label, _ = self._simple_rule(text)
        return label

    def predict_proba(self, text: str) -> float:
        # 使用随机扰动模拟模型置信度
        _, prob = self._simple_rule(text)
        return min(1.0, prob + random.uniform(-0.1, 0.1))

    @staticmethod
    def train_placeholder(training_file: str, model_path: str) -> None:
        """示例训练函数，实际可用 PyTorch DataLoader + 优化器实现。"""
        raise NotImplementedError("请在实际场景中实现 TextCNN 训练逻辑")


def demo_predict(text: str) -> Tuple[int, float]:
    clf = TextCNNClassifier(model_path="/tmp/non-exist.pt")
    return clf.predict(text), clf.predict_proba(text)
